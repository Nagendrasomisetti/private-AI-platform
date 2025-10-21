"""
Database connection API endpoints
"""
import uuid
from typing import Optional, Dict, Any
from urllib.parse import urlparse

import sqlalchemy
from sqlalchemy import create_engine, text
from fastapi import APIRouter, HTTPException

from ..models.schemas import DatabaseConnectionRequest, DatabaseConnectionResponse, ErrorResponse
from ..core.logging import get_logger

logger = get_logger("database_api")
router = APIRouter(prefix="/connect-db", tags=["database"])

# In-memory storage for connections (in production, use a proper database)
active_connections: Dict[str, Dict[str, Any]] = {}


@router.post("/", response_model=DatabaseConnectionResponse)
async def connect_database(request: DatabaseConnectionRequest):
    """
    Connect to a database and test the connection
    
    Args:
        request: Database connection request with URL and type
        
    Returns:
        DatabaseConnectionResponse: Connection status and metadata
    """
    try:
        logger.info("Database connection request received", db_url=request.db_url[:50] + "...")
        
        # Parse database URL
        parsed_url = urlparse(request.db_url)
        db_type = request.db_type or parsed_url.scheme
        
        # Validate database type
        supported_types = ["postgresql", "mysql", "sqlite", "sqlite3"]
        if db_type not in supported_types:
            raise ValueError(f"Unsupported database type: {db_type}. Supported types: {supported_types}")
        
        # Test connection
        engine = create_engine(request.db_url, echo=False)
        
        with engine.connect() as connection:
            # Test basic connectivity
            result = connection.execute(text("SELECT 1"))
            result.fetchone()
            
            # Get table information
            tables = []
            try:
                if db_type in ["postgresql"]:
                    # PostgreSQL table query
                    table_query = text("""
                        SELECT table_name 
                        FROM information_schema.tables 
                        WHERE table_schema = 'public'
                        ORDER BY table_name
                    """)
                elif db_type in ["mysql"]:
                    # MySQL table query
                    table_query = text("SHOW TABLES")
                elif db_type in ["sqlite", "sqlite3"]:
                    # SQLite table query
                    table_query = text("SELECT name FROM sqlite_master WHERE type='table'")
                else:
                    table_query = text("SELECT 1")  # Fallback
                
                table_result = connection.execute(table_query)
                tables = [row[0] for row in table_result.fetchall()]
                
            except Exception as e:
                logger.warning("Could not retrieve table list", error=str(e))
                tables = []
        
        # Generate connection ID
        connection_id = str(uuid.uuid4())
        
        # Store connection info
        active_connections[connection_id] = {
            "db_url": request.db_url,
            "db_type": db_type,
            "tables": tables,
            "status": "connected"
        }
        
        response = DatabaseConnectionResponse(
            status="success",
            message=f"Successfully connected to {db_type} database",
            connection_id=connection_id,
            tables=tables
        )
        
        logger.info("Database connection successful", 
                   connection_id=connection_id,
                   db_type=db_type,
                   table_count=len(tables))
        
        return response
        
    except sqlalchemy.exc.SQLAlchemyError as e:
        logger.error("Database connection failed - SQLAlchemy error", error=str(e))
        raise HTTPException(
            status_code=400, 
            detail=f"Database connection failed: {str(e)}"
        )
    
    except ValueError as e:
        logger.error("Database connection failed - validation error", error=str(e))
        raise HTTPException(status_code=400, detail=str(e))
    
    except Exception as e:
        logger.error("Database connection failed - unexpected error", error=str(e))
        raise HTTPException(
            status_code=500, 
            detail="Database connection failed due to an unexpected error"
        )


@router.get("/status/{connection_id}")
async def get_connection_status(connection_id: str):
    """
    Get the status of a database connection
    
    Args:
        connection_id: The connection ID to check
        
    Returns:
        dict: Connection status information
    """
    try:
        logger.info("Connection status requested", connection_id=connection_id)
        
        if connection_id not in active_connections:
            raise HTTPException(status_code=404, detail="Connection not found")
        
        connection_info = active_connections[connection_id]
        
        # Test if connection is still alive
        try:
            engine = create_engine(connection_info["db_url"], echo=False)
            with engine.connect() as connection:
                connection.execute(text("SELECT 1"))
            connection_info["status"] = "connected"
        except Exception:
            connection_info["status"] = "disconnected"
        
        return {
            "connection_id": connection_id,
            "status": connection_info["status"],
            "db_type": connection_info["db_type"],
            "tables": connection_info["tables"],
            "message": f"Connection is {connection_info['status']}"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get connection status", error=str(e), connection_id=connection_id)
        raise HTTPException(status_code=500, detail="Failed to get connection status")


@router.delete("/{connection_id}")
async def disconnect_database(connection_id: str):
    """
    Disconnect from a database
    
    Args:
        connection_id: The connection ID to disconnect
        
    Returns:
        dict: Disconnection status
    """
    try:
        logger.info("Database disconnection requested", connection_id=connection_id)
        
        if connection_id not in active_connections:
            raise HTTPException(status_code=404, detail="Connection not found")
        
        # Remove connection from active connections
        del active_connections[connection_id]
        
        logger.info("Database disconnected successfully", connection_id=connection_id)
        
        return {
            "status": "success",
            "message": f"Connection {connection_id} disconnected successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to disconnect database", error=str(e), connection_id=connection_id)
        raise HTTPException(status_code=500, detail="Failed to disconnect database")


@router.get("/")
async def list_connections():
    """
    List all active database connections
    
    Returns:
        dict: List of active connections
    """
    try:
        logger.info("List connections requested")
        
        connections = []
        for conn_id, conn_info in active_connections.items():
            connections.append({
                "connection_id": conn_id,
                "db_type": conn_info["db_type"],
                "tables": conn_info["tables"],
                "status": conn_info["status"]
            })
        
        return {
            "active_connections": connections,
            "total_connections": len(connections)
        }
        
    except Exception as e:
        logger.error("Failed to list connections", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to list connections")
