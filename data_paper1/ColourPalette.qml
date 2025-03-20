<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis version="3.24.1-Tisler" maxScale="0" minScale="1e+08" hasScaleBasedVisibilityFlag="0" styleCategories="AllStyleCategories">
  <flags>
    <Identifiable>1</Identifiable>
    <Removable>1</Removable>
    <Searchable>1</Searchable>
    <Private>0</Private>
  </flags>
  <temporal enabled="0" fetchMode="0" mode="0">
    <fixedRange>
      <start></start>
      <end></end>
    </fixedRange>
  </temporal>
  <customproperties>
    <Option type="Map">
      <Option type="bool" value="false" name="WMSBackgroundLayer"/>
      <Option type="bool" value="false" name="WMSPublishDataSourceUrl"/>
      <Option type="int" value="0" name="embeddedWidgets/count"/>
      <Option type="QString" value="Value" name="identify/format"/>
    </Option>
  </customproperties>
  <pipe-data-defined-properties>
    <Option type="Map">
      <Option type="QString" value="" name="name"/>
      <Option name="properties"/>
      <Option type="QString" value="collection" name="type"/>
    </Option>
  </pipe-data-defined-properties>
  <pipe>
    <provider>
      <resampling enabled="false" maxOversampling="2" zoomedOutResamplingMethod="nearestNeighbour" zoomedInResamplingMethod="nearestNeighbour"/>
    </provider>
    <rasterrenderer type="paletted" alphaBand="-1" opacity="1" nodataColor="" band="1">
      <rasterTransparency/>
      <minMaxOrigin>
        <limits>None</limits>
        <extent>WholeRaster</extent>
        <statAccuracy>Estimated</statAccuracy>
        <cumulativeCutLower>0.02</cumulativeCutLower>
        <cumulativeCutUpper>0.98</cumulativeCutUpper>
        <stdDevFactor>2</stdDevFactor>
      </minMaxOrigin>
      <colorPalette>
        <paletteEntry color="#641928" label="1" alpha="255" value="1"/>
        <paletteEntry color="#aa3c46" label="2" alpha="255" value="2"/>
        <paletteEntry color="#c35f6e" label="3" alpha="255" value="3"/>
        <paletteEntry color="#dc82aa" label="4" alpha="255" value="4"/>
        <paletteEntry color="#dcaa7d" label="5" alpha="255" value="5"/>
        <paletteEntry color="#824b2d" label="6" alpha="255" value="6"/>
        <paletteEntry color="#aac80f" label="7" alpha="255" value="7"/>
        <paletteEntry color="#8ce6a5" label="8" alpha="255" value="8"/>
        <paletteEntry color="#328719" label="9" alpha="255" value="9"/>
        <paletteEntry color="#28501e" label="10" alpha="255" value="10"/>
        <paletteEntry color="#41d755" label="11" alpha="255" value="11"/>
        <paletteEntry color="#826e6e" label="12" alpha="255" value="12"/>
        <paletteEntry color="#b4aa96" label="13" alpha="255" value="13"/>
        <paletteEntry color="#bef0f0" label="14" alpha="255" value="14"/>
        <paletteEntry color="#071400" label="15" alpha="255" value="15"/>
        <paletteEntry color="#071400" label="16" alpha="255" value="16"/>
        <paletteEntry color="#071400" label="17" alpha="255" value="17"/>
        <paletteEntry color="#071400" label="18" alpha="255" value="18"/>
        <paletteEntry color="#071400" label="19" alpha="255" value="19"/>
        <paletteEntry color="#071400" label="20" alpha="255" value="20"/>
        <paletteEntry color="#071400" label="21" alpha="255" value="21"/>
        <paletteEntry color="#071400" label="22" alpha="255" value="22"/>
        <paletteEntry color="#071400" label="23" alpha="255" value="23"/>
        <paletteEntry color="#46d2d2" label="24" alpha="255" value="24"/>
        <paletteEntry color="#46d2d2" label="25" alpha="255" value="25"/>
        <paletteEntry color="#46d2d2" label="26" alpha="255" value="26"/>
      </colorPalette>
      <colorramp type="randomcolors" name="[source]">
        <Option/>
      </colorramp>
    </rasterrenderer>
    <brightnesscontrast gamma="1" brightness="0" contrast="0"/>
    <huesaturation invertColors="0" colorizeGreen="128" colorizeBlue="128" colorizeStrength="100" colorizeRed="255" grayscaleMode="0" saturation="0" colorizeOn="0"/>
    <rasterresampler maxOversampling="2"/>
    <resamplingStage>resamplingFilter</resamplingStage>
  </pipe>
  <blendMode>0</blendMode>
</qgis>
