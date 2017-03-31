<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    version="2.0" xpath-default-namespace="http://www.tei-c.org/ns/1.0" xmlns:tei="http://www.tei-c.org/ns/1.0">
    
    
    <xsl:variable name="title"><xsl:value-of select="/TEI/teiHeader/fileDesc/titleStmt/title"/></xsl:variable>
    <xsl:variable name="author"><xsl:value-of select="/TEI/teiHeader/fileDesc/titleStmt/author"/></xsl:variable>
    <xsl:variable name="editor"><xsl:value-of select="/TEI/teiHeader/fileDesc/titleStmt/editor"/></xsl:variable>
    <xsl:param name="targetdirectory">null</xsl:param>
  <!-- get versioning numbers -->
    <xsl:param name="sourceversion"><xsl:value-of select="/TEI/teiHeader/fileDesc/editionStmt/edition/@n"/></xsl:param>
    
    <!-- this xsltconvnumber should be the same as the git tag, and for any commit past the tag should be the tag name plus '-dev' -->
    <xsl:param name="conversionversion">dev</xsl:param>
    
    <!-- default is dev; if a unique version number for the print output is desired; it should be passed as a parameter -->
    
    <!-- combined version number should have mirror syntax of an equation x+y source+conversion -->
    <xsl:variable name="combinedversionnumber"><xsl:value-of select="$sourceversion"/>+<xsl:value-of select="$conversionversion"/></xsl:variable>
    <!-- end versioning numbers -->  
    <xsl:variable name="fs"><xsl:value-of select="/TEI/text/body/div/@xml:id"/></xsl:variable>
    <xsl:variable name="name-list-file">/Users/jcwitt/Projects/lombardpress/lombardpress-lists/Prosopography.xml</xsl:variable>
    <xsl:variable name="work-list-file">/Users/jcwitt/Projects/lombardpress/lombardpress-lists/workscited.xml</xsl:variable>
    
    <xsl:output method="text" indent="no"/>
    <!-- <xsl:strip-space elements="*"/> -->
    
    <xsl:template match="text()">
    <xsl:value-of select="replace(., '\s+', ' ')"/>    
    </xsl:template>
    
    <xsl:template match="/">
        %this tex file was auto produced from TEI by lombardpress-print on <xsl:value-of  select="current-dateTime()"/> using the  <xsl:value-of select="base-uri(document(''))"/> 
        \documentclass[twoside, openright]{report}
        
        % etex package is added to fix bug with eledmac package and mac-tex 2015
        % See http://tex.stackexchange.com/questions/250615/error-when-compiling-with-tex-live-2015-eledmac-package
        \usepackage{etex}
        
        %imakeidx must be loaded beore eledmac
        \usepackage{imakeidx}
        
        \usepackage{eledmac}
        \usepackage{titlesec}
        \usepackage [latin]{babel}
        \usepackage [autostyle, english = american]{csquotes}
        \usepackage{geometry}
        \usepackage{fancyhdr}
        \usepackage[letter, center, cam]{crop}
        
        \usepackage{color}
        
        \geometry{paperheight=10in, paperwidth=7in, hmarginratio=3:2, inner=1.7in, outer=1.13in, bmargin=1in} 
        
        %fancyheading settings
        \pagestyle{fancy}
        
        %git package 
        \usepackage{gitinfo2}
        
        %watermark
        \usepackage{draftwatermark}
        <xsl:if test="/TEI/teiHeader/revisionDesc/@status = 'draft'">
          %\SetWatermarkText{Draft}
          %\SetWatermarkScale{.5}
          %\SetWatermarkAngle{0}
          %\SetWatermarkVerCenter{1 cm}
        </xsl:if>
        
        %quotes settings
        \MakeOuterQuote{"}
        
        %title settings
        \titleformat{\section} {\normalfont\scshape}{\thesection}{1em}{}
        \titlespacing\section{0pt}{12pt plus 4pt minus 2pt}{12pt plus 2pt minus 2pt}
        \titleformat{\chapter} {\normalfont\Large\uppercase}{\thechapter}{50pt}{}
        
        %eledmac settings
        \foottwocol{B}
        \linenummargin{outer}
        \sidenotemargin{inner}
        \numberlinefalse
        
        %other settings
        \linespread{1.1}
        
        %custom macros
        \newcommand{\name}[1]{\textsc{#1}}
        \newcommand{\worktitle}[1]{\textit{#1}}
        
        
        \begin{document}
        \fancyhead[RO]{<xsl:value-of select="$title"/>}
        \fancyhead[LO]{<xsl:value-of select="$author"/>}
        \fancyhead[LE]{<xsl:value-of select="$combinedversionnumber"/>+\gitDescribe}
        \chapter*{<xsl:value-of select="$title"/>}
        \addcontentsline{toc}{chapter}{<xsl:value-of select="$title"/>}
        
    	  <xsl:apply-templates select="//body"/>
        \end{document}
    </xsl:template>
    
    <xsl:template match="div//head">\section*{<xsl:apply-templates/>}</xsl:template>
    <xsl:template match="div//div">
        \bigskip
        <xsl:apply-templates/>
    </xsl:template>
		
	<xsl:template match="body//p[(count(//body//p) - count(following::p)) = 1]">
		<xsl:variable name="pn"><xsl:number level="any" from="tei:text"/></xsl:variable>
		<xsl:variable name="MsI">
			<xsl:value-of select="translate(/TEI/text/front/div[@type='startsOn']/cb/@ed, '#', '')"/>
		</xsl:variable>
		\pstart
		<xsl:if test="/TEI/text/front/div[@type='startsOn']/cb">
			Begins on: <xsl:value-of select="concat($MsI, /TEI/text/front/div[@type='startsOn']/cb/@n)"/>
			\\
		</xsl:if>
		\ledsidenote{\textbf{<xsl:value-of select="$pn"/>}}
		<xsl:apply-templates/>
		\pend
	</xsl:template>
	
    <xsl:template match="p">
        <xsl:variable name="pn"><xsl:number level="any" from="tei:text"/></xsl:variable>
        \pstart
        \ledsidenote{\textbf{<xsl:value-of select="$pn"/>}}
        <xsl:apply-templates/>
        \pend
    </xsl:template>
    <xsl:template match="head">
    </xsl:template>
    <xsl:template match="div">
    	\beginnumbering
        <xsl:apply-templates/>
    	\endnumbering
    </xsl:template>
    
    
    <xsl:template match="pb | cb">
    	<xsl:variable name="MsI"><xsl:value-of select="translate(./@ed, '#', '')"/></xsl:variable>\\
    	\\
    	<xsl:value-of select="concat($MsI, ./@n)"/>
    	\\
    </xsl:template>
    
    
    <xsl:template match="lb">\\ - </xsl:template>
    
		<xsl:template match="ref"><xsl:apply-templates/></xsl:template>
    
    
		<xsl:template match="del">
			<xsl:text>\textcolor{red}{</xsl:text>
			<xsl:apply-templates/>
			<xsl:text>}</xsl:text>
		</xsl:template>
		<xsl:template match="add">
			<xsl:text>\textcolor{red}{</xsl:text>
			<xsl:apply-templates/>
			<xsl:text>}</xsl:text>
		</xsl:template>
		<xsl:template match="unclear">
			<xsl:text>\textcolor{green}{</xsl:text>
			<xsl:apply-templates/>
			<xsl:text>}</xsl:text>
		</xsl:template>
    
    <xsl:template match="name">
        <xsl:variable name="nameid" select="substring-after(./@ref, '#')"/>
        <xsl:text>\name{</xsl:text>
        <xsl:apply-templates/>
        <xsl:text>}</xsl:text><xsl:text>\index[persons]{</xsl:text><xsl:value-of select="document($name-list-file)//tei:person[@xml:id=$nameid]/tei:persName[1]"/><xsl:text>}</xsl:text>
    </xsl:template>
    <xsl:template match="title">
        <xsl:variable name="workid" select="substring-after(./@ref, '#')"/>
        <xsl:text>\worktitle{</xsl:text>
        <xsl:apply-templates/>
      <xsl:text>}</xsl:text><xsl:text>\index[works]{</xsl:text><xsl:value-of select="document($work-list-file)//tei:bibl[@xml:id=$workid]/tei:title[1]"/><xsl:text>}</xsl:text>
    </xsl:template>
    
    
    
    <xsl:template match="quote"><xsl:apply-templates/></xsl:template>
		<xsl:template match="reg"></xsl:template>
		<xsl:template match="corr"></xsl:template>
		<xsl:template match="pc[@ana='#punctus']"></xsl:template>
		<xsl:template match="pc[@ana='#virgula']"></xsl:template>
		<xsl:template match="pc[@ana='#pilcrow']"></xsl:template>
	
	
   


</xsl:stylesheet>