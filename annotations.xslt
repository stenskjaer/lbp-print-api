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
    <xsl:variable name="name-list-file">/Users/jcwitt/Projects/lombardpress/lombardpress-lists/Prosopography.xml</xsl:variable>
    <xsl:variable name="work-list-file">/Users/jcwitt/Projects/lombardpress/lombardpress-lists/workscited.xml</xsl:variable>
  <xsl:variable name="source-list-file">/Users/jcwitt/Projects/lombardpress/sourceTitleMaps/test.xml</xsl:variable>
  
    <xsl:output method="text" indent="no"/>
    <!-- <xsl:strip-space elements="*"/> -->
    
    <xsl:template match="text()">
      <xsl:variable name="newText" select="replace(., '&amp;', ' \\&amp; ')"/>
      <xsl:variable name="newerText" select="replace($newText, '§', ' \\textsection ')"/>
      <xsl:value-of select="replace($newerText, '\s+', ' ')"/>
    </xsl:template>
    
    <xsl:template match="/">
        %this tex file was auto produced from TEI by lbp-print-xslt 1.0.0 critical stylesheets on <xsl:value-of  select="current-dateTime()"/> using the  <xsl:value-of select="base-uri(document(''))"/> 
        \documentclass[twoside, openright]{report}
        
        % etex package is added to fix bug with eledmac package and mac-tex 2015
        % See http://tex.stackexchange.com/questions/250615/error-when-compiling-with-tex-live-2015-eledmac-package
        \usepackage{etex}
        
        %imakeidx must be loaded beore eledmac
        \usepackage{imakeidx}
        
        \usepackage{reledmac}
        % adds linked internal references
        \usepackage[hidelinks]{hyperref}
        \usepackage{titlesec}
        
        \usepackage [latin]{babel}
        \usepackage[style=american] {csquotes}
        \usepackage{geometry}
        \usepackage{fancyhdr}
        \usepackage[letter, center, cam]{crop}
        
        
        \geometry{paperheight=10in, paperwidth=7in, hmarginratio=3:2, inner=1.7in, outer=1.13in, bmargin=1in} 
        
        %fancyheading settings
        \pagestyle{fancy}
        
        %git package 
        \usepackage{gitinfo2}
        
        %watermark
    		
   <!-- 		<xsl:if test="/TEI/teiHeader/revisionDesc/@status = 'draft'">
        \usepackage{draftwatermark}
        
        %\SetWatermarkText{Draft}
        %\SetWatermarkScale{.5}
        %\SetWatermarkAngle{0}
        %\SetWatermarkVerCenter{1 cm}
    		</xsl:if>-->
        
        
        %quotes settings
        \MakeOuterQuote{"}
        
        %package for angle brackets
        \usepackage{textcomp}
        
        %title settings
        \titleformat{\section} {\normalfont\scshape}{\thesection}{1em}{}
        \titlespacing\section{0pt}{12pt plus 4pt minus 2pt}{12pt plus 2pt minus 2pt}
        \titleformat{\chapter} {\normalfont\Large\uppercase}{\thechapter}{50pt}{}
        
        %reledmac settings % these settings change footnotes to run inline as a paragraph, 
        %change paragraph to twocol, threecol, or normal for different effects
        \Xarrangement[A]{paragraph}
        \Xarrangement[B]{paragraph}
        \Xnotenumfont[A]{\normalfont\bfseries}
        \Xnotenumfont[B]{\normalfont\bfseries}
        
        \linenummargin{outer}
        \sidenotemargin{inner}
        
        %other settings
        \linespread{1.1}
        
        %custom macros
        \newcommand{\name}[1]{\textsc{#1}}
        \newcommand{\worktitle}[1]{\textit{#1}}
        
        
        
        
        \newcommand{\crossref}[2]
        {
        \ifnum#1=000
          #2
        \else
          Vide #1
        \fi
        }
        
        
        
        
        \begin{document}
        <!--\fancyhead[RO]{<xsl:value-of select="$title"/>}
        \fancyhead[LO]{<xsl:value-of select="$author"/>}
        \fancyhead[LE]{<xsl:value-of select="$combinedversionnumber"/>+\gitDescribe}-->
        
        
      <xsl:variable name="jsondoc" select="json-to-xml(j:unparsed-text('/Users/jcwitt/Downloads/classReader-2020-12-22-test.json'))"/>
      <!-- <xsl:variable name="jsondoc" select="json-to-xml(j:unparsed-text('/Users/jcwitt/Downloads/porphyryReader-2021-09-30.json'))"/>  -->
        <xsl:for-each select="$jsondoc/j:array//j:map">
          <xsl:variable name="id" select="tokenize(./j:map[@key='target']/j:string[@key='source'], '/resource/')[2]"/>
          <xsl:message><xsl:value-of select="$id"/></xsl:message>
          <xsl:if test="$id and contains($id, 'transcription')">
            <xsl:variable name="doc" select="document(concat('http://exist.scta.info/exist/apps/scta-app/document/', $id))"/>
            <!--\chapter*{<xsl:value-of select="$doc/TEI/teiHeader/fileDesc/titleStmt/title"/>}-->
            \bigskip
            <xsl:value-of select="$doc/TEI/teiHeader/fileDesc/titleStmt/title"/>
            \bigskip
            \addcontentsline{toc}{chapter}{<xsl:value-of select="$doc/TEI/teiHeader/fileDesc/titleStmt/title"/>}
            <xsl:if test="./j:map[@key='body']/j:string[@key='value']">
              \bigskip
              Editor's note: <xsl:value-of select="./j:map[@key='body']/j:string[@key='value']"/>
              \bigskip
            </xsl:if>
            <xsl:apply-templates select="$doc//body"/>
          </xsl:if>
          <xsl:if test="./j:boolean[@key='target']/text() = 'false'">
            \bigskip
            Editor's note: <xsl:value-of select="./j:map[@key='body']/j:string[@key='value']"/>
            \bigskip
          </xsl:if>
        </xsl:for-each>
        
        
      
      
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
        \edlabel{http://scta.info/resource/<xsl:value-of select="./@xml:id"/>}
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
    
	<xsl:template match="pb">
		<xsl:choose>
			<xsl:when test="//cb">
			</xsl:when>
			<xsl:otherwise>
				<xsl:variable name="MsI">
					<xsl:value-of select="translate(./@ed, '#', '')"/>
				</xsl:variable>
				<xsl:variable name="number">
					<xsl:value-of select="./@n"/>
				</xsl:variable>
				\ledsidenote{<xsl:value-of select="concat($MsI, $number)"/>}
			</xsl:otherwise>
		</xsl:choose>
	</xsl:template>
	<xsl:template match="cb">
		<xsl:variable name="MsI">
			<xsl:value-of select="translate(./@ed, '#', '')"/>
		</xsl:variable>
		<xsl:variable name="MsI-with-hash">
			<xsl:value-of select="./@ed"/>
		</xsl:variable>
		<xsl:variable name="number">
			<xsl:value-of select="./preceding::pb[@ed=$MsI-with-hash][1]/@n"/>
		</xsl:variable>
		\ledsidenote{<xsl:value-of select="concat($MsI, $number[1],  ./@n)"/>}
	</xsl:template>
	
  <xsl:template match="supplied|corr">\textlangle{}<xsl:apply-templates/>\textrangle{}</xsl:template>
	
	<xsl:template match="cit[quote]">
	  <xsl:variable name="sourceid" select="./quote/@source"/>
	  <xsl:variable name="source-title" select="document($source-list-file)//sctastm:pair[sctastm:source=$sourceid]/sctastm:longTitle[1]"/>
	  <xsl:variable name="topLevelExpression-title" select="document($source-list-file)//sctastm:pair[sctastm:source=$sourceid]/sctastm:topLevelExpressionTitle[1]"/>
	  <xsl:variable name="author-title" select="document($source-list-file)//sctastm:pair[sctastm:source=$sourceid]/sctastm:authorTitle[1]"/>
	  <xsl:variable name="item-title" select="document($source-list-file)//sctastm:pair[sctastm:source=$sourceid]/sctastm:itemLevelExpressionTitle[1]"/>
	  <xsl:variable name="source-title-tokenized" select="tokenize($source-title, ',')"/>
	      <xsl:text>\edtext{\enquote{</xsl:text>
        <xsl:apply-templates select="quote"/>
        <xsl:text>}}{</xsl:text>
	       <!-- comments out lemma for quotes and references -->
        <!--<xsl:if test="count(tokenize(normalize-space(./quote), ' ')) &gt; 10">
            <xsl:text>\lemma{</xsl:text>
            <xsl:value-of select="tokenize(normalize-space(./quote), ' ')[1]"/>
           <xsl:text> \dots </xsl:text>
            <xsl:value-of select="tokenize(normalize-space(./quote), ' ')[last()]"/>
            <xsl:text>}</xsl:text>
        </xsl:if>-->
	       <!-- above is replaced by a blank lemma -->
	       <xsl:text>\lemma{}</xsl:text>
	      <xsl:text>\Afootnote[nosep]{</xsl:text>
     	  <xsl:choose>
     	    <xsl:when test="./quote/@source"><xsl:call-template name="crossRef"/></xsl:when>
     	    <xsl:otherwise><xsl:apply-templates select="bibl"/></xsl:otherwise>
     	  </xsl:choose>
	      <!-- uncomment belwo to show notes -->
	      <!--<xsl:if test="./note">
   	      <xsl:text> $\vert$ </xsl:text>
   	      <xsl:apply-templates select="note"/>
	      </xsl:if>-->
	  <xsl:text>}}</xsl:text><xsl:text>\index[sources]{</xsl:text><xsl:value-of select="concat($author-title, '!', $topLevelExpression-title, '!', $item-title)"/><xsl:text>}</xsl:text>
	  <!-- TODO UNCOMMENT WHEN YOU WANT TO ADD SOURCES INDEX WITH NEST; Seems like it will only work three nested deep -->
    </xsl:template>
		<xsl:template match="cit[ref]">
		  <xsl:variable name="sourceid" select="./ref/@target"/>
		  <xsl:variable name="source-title" select="document($source-list-file)//sctastm:pair[sctastm:source=$sourceid]/sctastm:longTitle[1]"/>
		  <xsl:variable name="topLevelExpression-title" select="document($source-list-file)//sctastm:pair[sctastm:source=$sourceid]/sctastm:topLevelExpressionTitle[1]"/>
		  <xsl:variable name="author-title" select="document($source-list-file)//sctastm:pair[sctastm:source=$sourceid]/sctastm:authorTitle[1]"/>
		  <xsl:variable name="item-title" select="document($source-list-file)//sctastm:pair[sctastm:source=$sourceid]/sctastm:itemLevelExpressionTitle[1]"/>
		  <xsl:variable name="source-title-tokenized" select="tokenize($source-title, ',')"/>
			<xsl:text>\edtext{</xsl:text>
			<xsl:apply-templates select="ref"/>
			<xsl:text>}{</xsl:text>
			<!--<xsl:if test="count(tokenize(normalize-space(./ref), ' ')) &gt; 10">
				<xsl:text>\lemma{</xsl:text>
				<xsl:value-of select="tokenize(normalize-space(./ref), ' ')[1]"/>
				<xsl:text> \dots </xsl:text>
				<xsl:value-of select="tokenize(normalize-space(./ref), ' ')[last()]"/>
				<xsl:text>}</xsl:text>
			</xsl:if>-->
		  <xsl:text>\lemma{}</xsl:text>
			<xsl:text>\Afootnote[nosep]{</xsl:text>
		  <xsl:choose>
		    <xsl:when test="./quote/@source"><xsl:call-template name="crossRef"/></xsl:when>
		    <xsl:otherwise><xsl:apply-templates select="bibl"/></xsl:otherwise>
		  </xsl:choose>
		  <!-- uncomment belwo to show notes -->
		  <!--<xsl:if test="./note">
  		  <xsl:text> $\vert$ </xsl:text>
  		  <xsl:apply-templates select="note"/>
		  </xsl:if>-->
		  <xsl:text>}}</xsl:text><xsl:text>\index[sources]{</xsl:text><xsl:value-of select="concat($author-title, '!', $topLevelExpression-title, '!', $item-title)"/><xsl:text>}</xsl:text>
		</xsl:template>
    
  <!--<xsl:template match="ref[bibl]">
        <xsl:text>\edtext{</xsl:text>
        <xsl:apply-templates select="seg"/>
        <xsl:text>}{</xsl:text>
        <xsl:if test="count(tokenize(normalize-space(./seg), ' ')) &gt; 10">
            <xsl:text>\lemma{</xsl:text>
            <xsl:value-of select="tokenize(normalize-space(./seg), ' ')[1]"/>
            <xsl:text> \dots </xsl:text>
            <xsl:value-of select="tokenize(normalize-space(./seg), ' ')[last()]"/>
            <xsl:text>}</xsl:text>
        </xsl:if>
        <xsl:text>\Afootnote{</xsl:text>
        <xsl:apply-templates select="bibl"/>
        
        <xsl:text>}}</xsl:text>
    </xsl:template>-->
    <xsl:template match="ref"><xsl:apply-templates/></xsl:template>
    <xsl:template match="app">
        <xsl:variable name="appnumber"><xsl:number level="any" from="tei:text"/></xsl:variable>
        <xsl:text>\edtext{</xsl:text>
        <xsl:apply-templates select="lem"/>
        <xsl:text>}{</xsl:text>
    		<xsl:choose>
        	<xsl:when test="count(tokenize(normalize-space(./lem), ' ')) &gt; 10">
            <xsl:text>\lemma{</xsl:text>
            <xsl:value-of select="tokenize(normalize-space(./lem), ' ')[1]"/>
            <xsl:text> \dots </xsl:text>
            <xsl:value-of select="tokenize(normalize-space(./lem), ' ')[last()]"/>
            <xsl:text>}</xsl:text>
        	</xsl:when>
    			<xsl:when test="not(./lem/node())">
    				<xsl:text>\lemma{</xsl:text>
    				<xsl:value-of select="./lem/@n"/>
    				<xsl:text>}</xsl:text>
    			</xsl:when>
    			<xsl:otherwise>
    				<xsl:text>\lemma{</xsl:text>
    				<!-- <xsl:value-of select="./lem"/> -->
    				<xsl:apply-templates select="lem"/>
    				<xsl:text>}</xsl:text>
    			</xsl:otherwise>
    			
    		</xsl:choose>
        <xsl:text>\Bfootnote{</xsl:text>
        <xsl:for-each select="./rdg">
        	<xsl:call-template name="varianttype"/>
        </xsl:for-each>
       <!-- uncomment belwo to show notes -->
       <!-- <xsl:if test="./note">
          <xsl:text> $\vert$ </xsl:text>
          <xsl:apply-templates select="note"/>
        </xsl:if>-->
      <!-- below adds a numbered to app entries, uncomment if you want number to show -->
      <!--<xsl:text>n</xsl:text><xsl:value-of select="$appnumber"></xsl:value-of>-->
        <xsl:text>}}</xsl:text>
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
  <xsl:template name="crossRef">
    \crossref{\xlineref{<xsl:value-of select="./quote/@source|./ref/@target"/>}}{<xsl:apply-templates select="bibl"/>}</xsl:template>
    <xsl:template match="quote"><xsl:apply-templates/></xsl:template>
    <xsl:template match="rdg"></xsl:template>
    <!--<xsl:template match="app/note"></xsl:template>-->
	
	<xsl:template name="varianttype">
		<!-- begin variation types -->
      <xsl:choose>
        <xsl:when test="./@type='variation-absent'">
            <xsl:text>\textit{om.} </xsl:text>
            <xsl:value-of select="translate(./@wit, '#', '')"/>
            <xsl:text> </xsl:text>
        </xsl:when>
      	<xsl:when test="./@type='variation-present'">
      		<xsl:choose>
      			<xsl:when test="./@cause='repetition'">
      				<xsl:text> \textit{iterum} </xsl:text>
      				<xsl:value-of select="translate(@wit, '#', '')"/><xsl:text> </xsl:text>
      			</xsl:when>
      			<xsl:otherwise>
      				<xsl:text> </xsl:text>
      				<xsl:value-of select="."/>
      				<xsl:text> \textit{in textu} </xsl:text>
      				<xsl:value-of select="translate(@wit, '#', '')"/>
      				<xsl:text> </xsl:text>
      			</xsl:otherwise>
      		</xsl:choose>
      	</xsl:when>
        <xsl:when test="./@type='variation-choice'">
          <xsl:text> \textit{plus lectiones} </xsl:text>
          <xsl:for-each select="./choice/seg">
            <xsl:text> </xsl:text> <xsl:value-of select="."/> <xsl:text> </xsl:text>
          </xsl:for-each>
          <xsl:value-of select="translate(@wit, '#', '')"/><xsl:text> </xsl:text>
          
        </xsl:when>
      	<xsl:when test="./@type='variation-substance'">
      		<xsl:text> </xsl:text><xsl:value-of select="."/><xsl:text> </xsl:text>
      		<xsl:value-of select="translate(@wit, '#', '')"/><xsl:text> </xsl:text>
      	</xsl:when>
      	<xsl:when test="./@type='variation-orthography'">
      		<xsl:text> </xsl:text><xsl:value-of select="."/><xsl:text> </xsl:text>
      		<xsl:value-of select="translate(@wit, '#', '')"/><xsl:text> </xsl:text>
      	</xsl:when>
        
      	<!-- begin correction types -->
      	<xsl:when test="./@type='correction-deletion'">
      		<xsl:value-of select="./del"/>
      		<xsl:text> \textit{add. sed del.} </xsl:text>
      		<xsl:value-of select="translate(@wit, '#', '')"/>
      		<xsl:text> </xsl:text>
      	</xsl:when>
      	<xsl:when test="./@type='correction-addition'">
      		<xsl:value-of select="./add"/>
      		<xsl:text> \textit{add.} </xsl:text> 
      		<xsl:choose>
      			<xsl:when test="./add/@place='above-line'">
      				<xsl:text>\textit{interl.} </xsl:text>
      			</xsl:when>
      			<xsl:when test="contains(./add/@place, 'margin')">
      				<xsl:text>\textit{in marg.} </xsl:text>
      			</xsl:when>
      		</xsl:choose>
      		<xsl:value-of select="translate(@wit, '#', '')"/><xsl:text> </xsl:text>
      	</xsl:when>
        <xsl:when test="./@type='correction-substitution'">
      		<xsl:text> </xsl:text><xsl:value-of select="./subst/add"/>
      		<xsl:text> \textit{corr. ex} </xsl:text>
      		<xsl:value-of select="./subst/del"/><xsl:text> </xsl:text>
      		<xsl:value-of select="translate(@wit, '#', '')"/><xsl:text> </xsl:text>
      	</xsl:when>
        <xsl:when test="./@type='correction-transposition'">
          <xsl:text> </xsl:text><xsl:value-of select="./subst/add"/>
          <xsl:text> \textit{corr. ex} </xsl:text>
          <xsl:value-of select="./subst/del"/><xsl:text> </xsl:text>
          <xsl:value-of select="translate(@wit, '#', '')"/><xsl:text> </xsl:text>
        </xsl:when>
      	<!-- fall back for case where @typ is not given -->
        <xsl:otherwise>
            <xsl:text> </xsl:text><xsl:value-of select="."/><xsl:text> </xsl:text>
            <xsl:value-of select="translate(@wit, '#', '')"/><xsl:text> </xsl:text>
        </xsl:otherwise>
    </xsl:choose>
</xsl:template>
</xsl:stylesheet>