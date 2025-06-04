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
  
  <xsl:output method="xhtml" indent="no"/>
  <xsl:template match="/">
    <html xmlns="http://www.w3.org/1999/xhtml">
      <head>
        <title>Test</title>
      </head>
      <body>
      
     
        
        
      <xsl:variable name="jsondoc" select="json-to-xml(j:unparsed-text($annolistfull))"/>
      <!-- <xsl:variable name="jsondoc" select="json-to-xml(j:unparsed-text('/Users/jcwitt/Downloads/porphyryReader-2021-09-30.json'))"/>  -->
        <xsl:for-each select="$jsondoc/j:array//j:map">
          <div>
          <xsl:variable name="id" select="tokenize(./j:map[@key='target']/j:string[@key='source'], '/resource/')[2]"/>
          <xsl:message><xsl:value-of select="$id"/></xsl:message>
          <xsl:if test="$id and contains($id, 'transcription')">
            <xsl:variable name="doc" select="document(concat('https://exist.scta.info/exist/apps/scta-app/document/', $id))"/>
            <h1><xsl:value-of select="$doc/TEI/teiHeader/fileDesc/titleStmt/title"/></h1>
            <xsl:if test="./j:map[@key='body']/j:string[@key='value']">
              <p>Editor's note: <xsl:value-of select="./j:map[@key='body']/j:string[@key='value']"/></p>
            </xsl:if>
            <xsl:apply-templates select="$doc//body"/>
          </xsl:if>
          </div>
        </xsl:for-each>
      </body>
    </html>
    
  </xsl:template>
  <xsl:template match="div">
    <div id="{@xml:id}">
      <xsl:apply-templates/>
    </div>
  </xsl:template>
  <xsl:template match="head[not(@type='question-title')]">
    <h1>
      <xsl:apply-templates/>
    </h1>
  </xsl:template>
  <xsl:template match="head[@type='question-title']">
    <h2>
      <xsl:apply-templates/>
    </h2>
  </xsl:template>
  <xsl:template match="p">
    <p id="{@xml:id}">
      <xsl:apply-templates/>
    </p>
  </xsl:template>
  <xsl:template match="quote">
    <span id="{@xml:id}">"<xsl:apply-templates/>"</span>
  </xsl:template>
  <xsl:template match="pb"/>
  <xsl:template match="cb"/>
  <xsl:template match="lb"/>
  <xsl:template match="rdg"/>
  <xsl:template match="note"/>
  <xsl:template match="bibl"/>
</xsl:stylesheet>