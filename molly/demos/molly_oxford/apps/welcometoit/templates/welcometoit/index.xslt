<?xml version="1.0"?>

<xsl:stylesheet version="1.0"
xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
xmlns:molly="http://mollyproject.org/xpath#">

<xsl:template match="/">
  <div class="section">
    <div class="header">
      <h2>
        <xsl:choose>
          <xsl:when test=".//div[@id='maincontent']/h2">
            <xsl:value-of select=".//div[@id='maincontent']/h2"/>
          </xsl:when>
          <xsl:otherwise>
            <xsl:value-of select=".//div[@id='maincontent']/h1"/>
          </xsl:otherwise>
        </xsl:choose>
      </h2>
    </div>

    <div>   
      <xsl:attribute name="class">
        <xsl:text>section-content</xsl:text>
        <xsl:if test=".//ul[@class='toc']">
          <xsl:text> no-round-bottom</xsl:text>
        </xsl:if>
      </xsl:attribute>
 
      <xsl:apply-templates select=".//div[@id='maincontent']"/>
    </div>
    
    <xsl:if test=".//ul[@class='toc']">
      <ul class="link-list">
        <xsl:apply-templates select=".//ul[@class='toc']/li"/>
      </ul>
    </xsl:if>
  </div>
</xsl:template>

<xsl:template match="a[@href]">
  <xsl:variable name="external" select="starts-with(@href, 'http://') or starts-with(@href, 'https://') or starts-with(@href, '/')"/>
  
  <a>
    <xsl:copy-of select="@title"/>
    
    
    <xsl:choose>
      <xsl:when test="$external">
        <xsl:copy-of select="@href"/>
      </xsl:when>
      <xsl:when test=".='index.xml'">
        <xsl:attribute name="href">
          <xsl:value-of select="molly:url(., 'welcometoit:index')"/>
        </xsl:attribute>
      </xsl:when>
      <xsl:when test="contains(@href, '.xml.ID=')">
        <xsl:attribute name="href">
          <xsl:value-of select="molly:url(@href, 'welcometoit:index', substring-before(@href, '.xml'), substring-after(@href, '.xml.ID='))"/>
        </xsl:attribute>
        <xsl:attribute name="foo">bar</xsl:attribute>
      </xsl:when>
      <xsl:otherwise>
        <xsl:attribute name="href">
          <xsl:value-of select="molly:url(@href, 'welcometoit:index', substring-before(@href, '.xml'))"/>
        </xsl:attribute>
      </xsl:otherwise>
    </xsl:choose>
    
    <xsl:apply-templates match="text() | *"/>
    
    <xsl:if test="$external">
      <xsl:text> </xsl:text>
      <small><i>(external)</i></small>
    </xsl:if>
  </a>
</xsl:template>

<xsl:template match="h1 | h2 | img | ul[@class='toc']"/>

<xsl:template match="ul[name(..)='dd']">
  <ul style="padding-left:2em; list-style:none; margin-top:4px">
    <xsl:apply-templates select="text() | node()"/>
  </ul>
</xsl:template>

<xsl:template match="li[name(../..)='dd']">
  <li style="text-indent:-1em;">
    <xsl:apply-templates select="text() | node()"/>
  </li>
</xsl:template>

<xsl:template match="dt">
  <dt style="margin-top:12px; font-weight:bold">
    <xsl:apply-templates select="text() | node()"/>
  </dt>
</xsl:template>

<xsl:template match="dd[../../@id='maincontent']">
  <dd style="margin-left:0">
    <span style="font-style:italic"><xsl:copy-of select="text()"/></span>
    <xsl:apply-templates select="*"/>
  </dd>
</xsl:template>

<xsl:template match="div[@class='left'][img]"/>

<xsl:template match="text()">
  <xsl:choose>
    <xsl:when test="contains(., 'Sections in this document')"/>
    <xsl:otherwise><xsl:copy/></xsl:otherwise>
  </xsl:choose>
</xsl:template>

<xsl:template match="div[@id='map']">
  <script src="http://maps.google.com/maps?file=api&amp;v=2&amp;key=ABQIAAAAXWaYpACABYqQEjTJ7Xh76RQRDGKfPCBPJx7V3XOgbmepBWFGzRQ2l9HRmkLXUwGWT5ZZS4ZWjBM9hQ" type="text/javascript"></script><script type="text/javascript"> //

    function load() {
      if (GBrowserIsCompatible()) {

    var CustomGetTileUrl = function(a,b){

       return 'http://a.tile.openstreetmap.org/'+b+'/'+a.x+'/'+a.y+'.png';
    
    }

    var copyright = new GCopyright(1, new GLatLngBounds(new GLatLng(53.8136257,-3.0981445),
						    new GLatLng(53.8654855,-2.9663944) ),
			       17, "");

			    
    var copyrightCollection = new GCopyrightCollection('');
    copyrightCollection.addCopyright(copyright);

    var tilelayers = [new GTileLayer(copyrightCollection,1,17)];
    tilelayers[0].getTileUrl = CustomGetTileUrl;
    var osmmap = new GMapType(tilelayers, G_SATELLITE_MAP.getProjection(), "OSM");


        var map = new GMap2(document.getElementById("map"));
        map.addControl(new GSmallMapControl());
         map.setCenter(new GLatLng(51.760053,-1.2604), 15);
	var point = new GLatLng(51.760053,-1.2604);
	map.addOverlay(new GMarker(point,{title:"OUCS"}));
	map.addMapType(osmmap);
	map.setMapType(osmmap);
      }
    }
    
    $(load);

    //
  	</script>
  	<div id="map" style="width: 100%; height: 300px; position: relative; background-color: rgb(229, 227, 223);"/>
</xsl:template>

<xsl:template match="p[@class='right']"/>

<xsl:template match="div[@class='p']">
  <p>
    <xsl:apply-templates select="text() | @* | *"/>
  </p>
</xsl:template>

<!--
<xsl:template match="@src">
  <xsl:attribute name="src">
    <xsl:value-of select="concat('http://www.oucs.ox.ac.uk/welcometoit/', .)"/>
  </xsl:attribute>
</xsl:template>
-->

<xsl:template match="node() | @*">
  <xsl:copy>
    <xsl:apply-templates select="node() | @*"/>
  </xsl:copy>
</xsl:template>

</xsl:stylesheet>