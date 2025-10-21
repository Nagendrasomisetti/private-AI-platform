# PrivAI Desktop Assets

This directory contains assets for the PrivAI desktop application packaging and distribution.

## Required Assets

### Icons
- `icon.ico` - Windows icon (256x256, 128x128, 64x64, 48x48, 32x32, 16x16)
- `icon.icns` - macOS icon (512x512, 256x256, 128x128, 64x64, 32x32, 16x16)
- `icon.png` - Linux icon (512x512, 256x256, 128x128, 64x64, 32x32, 16x16)

### macOS Assets
- `entitlements.mac.plist` - macOS entitlements file
- `dmg-background.png` - DMG background image (600x400)

### Windows Assets
- `icon.ico` - Windows application icon

### Linux Assets
- `icon.png` - Linux application icon

## Icon Specifications

### Windows (.ico)
- Multiple sizes: 16x16, 32x32, 48x48, 64x64, 128x128, 256x256
- 32-bit color depth with alpha channel
- ICO format

### macOS (.icns)
- Multiple sizes: 16x16, 32x32, 64x64, 128x128, 256x256, 512x512
- 32-bit color depth with alpha channel
- ICNS format

### Linux (.png)
- Single size: 512x512
- 32-bit color depth with alpha channel
- PNG format

## Creating Icons

### From SVG
1. Create a high-resolution SVG (512x512 or larger)
2. Export to PNG at various sizes
3. Convert to ICO/ICNS using online tools or software

### Online Tools
- [ConvertICO](https://convertico.com/) - Convert PNG to ICO
- [CloudConvert](https://cloudconvert.com/) - Convert PNG to ICNS
- [IconKitchen](https://icon.kitchen/) - Generate multiple formats

### Software
- **Windows**: GIMP, Paint.NET, Adobe Illustrator
- **macOS**: Preview, Adobe Illustrator, Sketch
- **Linux**: GIMP, Inkscape, Adobe Illustrator

## DMG Background

The DMG background image should be:
- 600x400 pixels
- PNG format
- Include app icon and drag instructions
- Match the application's design theme

## Entitlements

The macOS entitlements file should include:
- Network access permissions
- File system access permissions
- Security requirements for code signing

## Notes

- All icons should maintain the same visual design
- Use high contrast for better visibility
- Test icons at different sizes to ensure clarity
- Follow platform-specific design guidelines
