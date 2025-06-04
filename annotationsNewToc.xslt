<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  version="3.0"
  xmlns:j="http://www.w3.org/2005/xpath-functions"
  xpath-default-namespace="http://www.tei-c.org/ns/1.0" xmlns:tei="http://www.tei-c.org/ns/1.0" xmlns:sctastm="http://scta.info/ns/source-title-map">
    
<!--    <xsl:param name="apploc"><xsl:value-of select="/TEI/teiHeader/encodingDesc/variantEncoding/@location"/></xsl:param>
    <xsl:param name="notesloc"><xsl:value-of select="/TEI/teiHeader/encodingDesc/variantEncoding/@location"/></xsl:param>
    <xsl:variable name="title"><xsl:value-of select="/TEI/teiHeader/fileDesc/titleStmt/title"/></xsl:variable>
    <xsl:variable name="author"><xsl:value-of select="/TEI/teiHeader/fileDesc/titleStmt/author"/></xsl:variable>
    <xsl:variable name="editor"><xsl:value-of select="/TEI/teiHeader/fileDesc/titleStmt/editor"/></xsl:variable>
    <xsl:param name="targetdirectory">null</xsl:param>
  <!-\- get versioning numbers -\->
    <xsl:param name="sourceversion"><xsl:value-of select="/TEI/teiHeader/fileDesc/editionStmt/edition/@n"/></xsl:param>
    
    <!-\- this xsltconvnumber should be the same as the git tag, and for any commit past the tag should be the tag name plus '-dev' -\->
    <xsl:param name="conversionversion">dev</xsl:param>
    
    <!-\- default is dev; if a unique version number for the print output is desired; it should be passed as a parameter -\->
    
    <!-\- combined version number should have mirror syntax of an equation x+y source+conversion -\->
    <xsl:variable name="combinedversionnumber"><xsl:value-of select="$sourceversion"/>+<xsl:value-of select="$conversionversion"/></xsl:variable>
    <!-\- end versioning numbers -\->  
    <xsl:variable name="fs"><xsl:value-of select="/TEI/text/body/div/@xml:id"/></xsl:variable> -->
    <!-- <xsl:variable name="name-list-file">/Users/jcwitt/Projects/lombardpress/lombardpress-lists/Prosopography.xml</xsl:variable>
    <xsl:variable name="work-list-file">/Users/jcwitt/Projects/lombardpress/lombardpress-lists/workscited.xml</xsl:variable>-->
     <xsl:variable name="source-list-file">./cache/sourceTitleMap.xml</xsl:variable>
  <!--<xsl:variable name="source-list-file">/Users/jcwitt/Projects/lombardpress/lbp-print-cache/sourceTitleMap.xml</xsl:variable>-->
<xsl:param name="annolist">cache/annotations.json</xsl:param>
<xsl:variable name="annolistfull">/usr/src/app/<xsl:value-of select="$annolist"/></xsl:variable>
  <!--<xsl:variable name="annolistfull">/Users/jcwitt/Desktop/annotationsTest.json</xsl:variable>-->
  
  <xsl:output method="xml" indent="yes"/>
  <xsl:template match="/">
    <ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1">
      <head>
        <meta name="dtb:uid" content="urn:uuid:123456"/>
        <meta name="dtb:depth" content="1"/>
        <meta name="dtb:totalPageCount" content="0"/>
        <meta name="dtb:maxPageNumber" content="0"/>
      </head>
      
     
        
        
      <xsl:variable name="jsondoc" select="json-to-xml(j:unparsed-text($annolistfull))"/>
      <!-- <xsl:variable name="jsondoc" select="json-to-xml(j:unparsed-text('/Users/jcwitt/Downloads/porphyryReader-2021-09-30.json'))"/>  -->
        <xsl:for-each select="$jsondoc/j:array//j:map">
          
          
          <xsl:variable name="id" select="tokenize(./j:map[@key='target']/j:string[@key='source'], '/resource/')[2]"/>
          <xsl:message><xsl:value-of select="$id"/></xsl:message>
          <xsl:if test="$id and contains($id, 'transcription')">
            <navMap>
            <xsl:variable name="doc" select="document(concat('https://exist.scta.info/exist/apps/scta-app/document/', $id))"/>
            <navPoint id="navPoint-{$id}" playOrder="1">
              <navLabel><xsl:value-of select="$doc/TEI/teiHeader/fileDesc/titleStmt/title"/></navLabel>
              <content src="content.xhtml#{$id}"/>
              <xsl:apply-templates select="$doc//body/div"/>
            </navPoint>
            <!--<xsl:apply-templates select="$doc//div"/>-->
            </navMap>
          </xsl:if>
          
        </xsl:for-each>
    </ncx>
    
  </xsl:template>
  <xsl:template match="div">
    <xsl:variable name="level"><xsl:value-of select="count(preceding::div) + 2 + count(ancestor::div)"/></xsl:variable>
    <navMap>
      <navPoint id="{@xml:id}" playOrder="{$level}">
        <navLabel><text><xsl:value-of select="./head[not(@type='question-title')]"/></text></navLabel>
        <content src="content.xhtml#{@xml:id}"/>
        <!-- <xsl:apply-templates select="div"/> -->
      </navPoint>
    </navMap>
    
  </xsl:template>
  
</xsl:stylesheet>