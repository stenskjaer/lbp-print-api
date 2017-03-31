<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    version="2.0" xpath-default-namespace="http://www.tei-c.org/ns/1.0" xmlns:tei="http://www.tei-c.org/ns/1.0">
    
    <xsl:param name="apploc"><xsl:value-of select="/TEI/teiHeader/encodingDesc/variantEncoding/@location"/></xsl:param>
    <xsl:param name="notesloc"><xsl:value-of select="/TEI/teiHeader/encodingDesc/variantEncoding/@location"/></xsl:param>
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
        \usepackage [english]{babel}
        \usepackage [autostyle, english = american]{csquotes}
        \usepackage{geometry}
        \usepackage{fancyhdr}
        \usepackage[letter, center, cam]{crop}
        
        
        \geometry{paperheight=10in, paperwidth=7in, hmarginratio=3:2, inner=1.7in, outer=1.13in, bmargin=1in} 
        
        %fancyheading settings
        \pagestyle{fancy}
        
        %git package 
        \usepackage{gitinfo2}
        
        %watermark
        \usepackage{draftwatermark}
        <xsl:if test="/TEI/teiHeader/revisionDesc/@status = 'draft'">
          \SetWatermarkText{Draft}
          \SetWatermarkScale{.5}
          \SetWatermarkAngle{0}
          \SetWatermarkVerCenter{1 cm}
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
    
    <xsl:template match="pb | cb"><xsl:variable name="MsI"><xsl:value-of select="translate(./@ed, '#', '')"/></xsl:variable>\ledsidenote{<xsl:value-of select="concat($MsI, ./@n)"/>}</xsl:template>
    <xsl:template match="supplied">[<xsl:apply-templates/>]</xsl:template>
    <xsl:template match="cit[quote]">
        <xsl:text>\edtext{\enquote{</xsl:text>
        <xsl:apply-templates select="quote"/>
        <xsl:text>}}{</xsl:text>
        <xsl:if test="count(tokenize(normalize-space(./quote), ' ')) &gt; 10">
            <xsl:text>\lemma{</xsl:text>
            <xsl:value-of select="tokenize(normalize-space(./quote), ' ')[1]"/>
           <xsl:text> \dots\ </xsl:text>
            <xsl:value-of select="tokenize(normalize-space(./quote), ' ')[last()]"/>
            <xsl:text>}</xsl:text>
        </xsl:if>
        <xsl:text>\Afootnote{</xsl:text>
        <xsl:apply-templates select="bibl"/>
        <xsl:text>}}</xsl:text>
    </xsl:template>
		<xsl:template match="cit[ref]">
			<xsl:text>\edtext{</xsl:text>
			<xsl:apply-templates select="ref"/>
			<xsl:text>}{</xsl:text>
			<xsl:if test="count(tokenize(normalize-space(./ref), ' ')) &gt; 10">
				<xsl:text>\lemma{</xsl:text>
				<xsl:value-of select="tokenize(normalize-space(./ref), ' ')[1]"/>
				<xsl:text> \dots\ </xsl:text>
				<xsl:value-of select="tokenize(normalize-space(./ref), ' ')[last()]"/>
				<xsl:text>}</xsl:text>
			</xsl:if>
			<xsl:text>\Afootnote{</xsl:text>
			<xsl:apply-templates select="bibl"/>
			<xsl:text>}}</xsl:text>
		</xsl:template>
    <xsl:template match="ref[bibl]">
        <xsl:text>\edtext{</xsl:text>
        <xsl:apply-templates select="seg"/>
        <xsl:text>}{</xsl:text>
        <xsl:if test="count(tokenize(normalize-space(./seg), ' ')) &gt; 10">
            <xsl:text>\lemma{</xsl:text>
            <xsl:value-of select="tokenize(normalize-space(./seg), ' ')[1]"/>
            <xsl:text> \dots\ </xsl:text>
            <xsl:value-of select="tokenize(normalize-space(./seg), ' ')[last()]"/>
            <xsl:text>}</xsl:text>
        </xsl:if>
        <xsl:text>\Afootnote{</xsl:text>
        <xsl:apply-templates select="bibl"/>
        <xsl:text>}}</xsl:text>
    </xsl:template>
    <xsl:template match="ref"><xsl:apply-templates/></xsl:template>
    <xsl:template match="app">
        <xsl:variable name="appnumber"><xsl:number level="any" from="tei:text"/></xsl:variable>
        <xsl:text>\edtext{</xsl:text>
        <xsl:apply-templates select="lem"/>
        <xsl:text>}{</xsl:text>
        <xsl:if test="count(tokenize(normalize-space(./lem), ' ')) &gt; 10">
            <xsl:text>\lemma{</xsl:text>
            <xsl:value-of select="tokenize(normalize-space(./lem), ' ')[1]"/>
            <xsl:text> \dots\ </xsl:text>
            <xsl:value-of select="tokenize(normalize-space(./lem), ' ')[last()]"/>
            <xsl:text>}</xsl:text>
        </xsl:if>
        <xsl:text>\Bfootnote{</xsl:text>
        <xsl:for-each select="./rdg"><xsl:call-template name="varianttype"/></xsl:for-each>
        <xsl:text>n</xsl:text><xsl:value-of select="$appnumber"></xsl:value-of><xsl:text>}}</xsl:text>
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
    <xsl:template match="mentioned">
        <xsl:text>\enquote*{</xsl:text>
        <xsl:apply-templates/>
        <xsl:text>}</xsl:text>
    </xsl:template>
    
    <xsl:template match="quote"><xsl:apply-templates/></xsl:template>
    <xsl:template match="rdg"></xsl:template>
    <xsl:template match="app/note"></xsl:template>

<xsl:template name="varianttype">
      <xsl:choose>
            <xsl:when test="contains(@type, 'om.') or ./@type='omission' or ./@type='omit'">
                <xsl:text>\textit{om.} </xsl:text>
                <xsl:value-of select="translate(./@wit, '#', '')"/>
                <xsl:text> </xsl:text>
            </xsl:when>
      			<xsl:when test="contains(@type, 'add.sed.del.') or ./@type='corrDeletion'"> <!-- eventually the "contains" options should be removed as "corrDeletion, corrAddition" becomes the standard in the app schema -->
                <xsl:value-of select="./corr/del"/>
                <xsl:text> \textit{add. sed del.} </xsl:text>
                <xsl:value-of select="translate(@wit, '#', '')"/>
                <xsl:text> </xsl:text>
            </xsl:when>
		      	<xsl:when test="./@type='correction-deletion'">
		      		<xsl:value-of select="./del"/>
		      		<xsl:text> \textit{add. sed del.} </xsl:text>
		      		<xsl:value-of select="translate(@wit, '#', '')"/>
		      		<xsl:text> </xsl:text>
		      	</xsl:when>
      			<xsl:when test="contains(@type, 'addCorrection') or ./@type='corrAddition'">
                <xsl:value-of select="./corr/add"/>
                <xsl:text> \textit{add.} </xsl:text> 
                <xsl:choose>
                    <xsl:when test="./corr/add/@place='aboveLine'">
                        <xsl:text>\textit{interl.} </xsl:text>
                    </xsl:when>
                    <xsl:when test="contains(./corr/add/@place, 'margin')">
                        <xsl:text>\textit{in marg.} </xsl:text>
                    </xsl:when>
                </xsl:choose>
                <xsl:value-of select="translate(@wit, '#', '')"/><xsl:text> </xsl:text>
            </xsl:when>
		      	<xsl:when test="./@type='correction-addition'">
		      		<xsl:value-of select="./add"/>
		      		<xsl:text> \textit{add.} </xsl:text> 
		      		<xsl:choose>
		      			<xsl:when test="./add/@place='aboveLine'">
		      				<xsl:text>\textit{interl.} </xsl:text>
		      			</xsl:when>
		      			<xsl:when test="contains(./add/@place, 'margin')">
		      				<xsl:text>\textit{in marg.} </xsl:text>
		      			</xsl:when>
		      		</xsl:choose>
		      		<xsl:value-of select="translate(@wit, '#', '')"/><xsl:text> </xsl:text>
		      	</xsl:when>
            <xsl:when test="contains(@type, 'rep.')">
                <xsl:text> \textit{rep.} </xsl:text>
                <xsl:value-of select="translate(@wit, '#', '')"/><xsl:text> </xsl:text>
            </xsl:when>
            <xsl:when test="contains(@type, 'intextu')">
                <xsl:text> </xsl:text>
                <xsl:value-of select="."/>
                <xsl:text> \textit{in textu} </xsl:text>
                <xsl:value-of select="translate(@wit, '#', '')"/>
                <xsl:text> </xsl:text>
           </xsl:when>
      			<xsl:when test="./@type='addition'">
		      		<xsl:text> </xsl:text>
		      		<xsl:value-of select="."/>
		      		<xsl:text> \textit{add.} </xsl:text>
		      		<xsl:value-of select="translate(@wit, '#', '')"/>
		      		<xsl:text> </xsl:text>
		      	</xsl:when>
      			<xsl:when test="contains(@type, 'corr.') or ./@type='corrReplace'">
                <xsl:text> </xsl:text><xsl:value-of select="./corr/add"/>
                <xsl:text> \textit{corr. ex} </xsl:text>
                <xsl:value-of select="./corr/del"/><xsl:text> </xsl:text>
                <xsl:value-of select="translate(@wit, '#', '')"/><xsl:text> </xsl:text>
            </xsl:when>
		      	<xsl:when test="./@type='correction-substitution'">
		      		<xsl:text> </xsl:text><xsl:value-of select="./subst/add"/>
		      		<xsl:text> \textit{corr. ex} </xsl:text>
		      		<xsl:value-of select="./subst/del"/><xsl:text> </xsl:text>
		      		<xsl:value-of select="translate(@wit, '#', '')"/><xsl:text> </xsl:text>
		      	</xsl:when>
            <xsl:otherwise>
                <xsl:text> </xsl:text><xsl:value-of select="."/><xsl:text> </xsl:text>
                <xsl:value-of select="translate(@wit, '#', '')"/><xsl:text> </xsl:text>
            </xsl:otherwise>
        </xsl:choose>
</xsl:template>
</xsl:stylesheet>