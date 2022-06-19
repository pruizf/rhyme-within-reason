<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:xs="http://www.w3.org/2001/XMLSchema" exclude-result-prefixes="xs"
    xpath-default-namespace="http://www.tei-c.org/ns/1.0" version="3.0">
    <xsl:output method="text"/>
    <xsl:variable name="text">
        <xsl:apply-templates mode="text" select="//lg"/>
    </xsl:variable>    
    <xsl:variable name="fileName" select="base-uri(.) => substring-before('.xml') => substring-after('source_with_rhyme/')"/>
    <xsl:variable name="authorId" select="$fileName => substring-before('_')"/>
    <xsl:template match="/">
        <xsl:result-document href="{$fileName}.txt">
            <xsl:apply-templates select="//w"/>
        </xsl:result-document>
    </xsl:template>
    <xsl:template match="w">
        <xsl:variable name="del" as="xs:string" select="'&#9;'"/>
        <xsl:variable name="id" select="generate-id(.)" as="xs:string"/>
        <xsl:variable name="incipit" select="ancestor::body/lg[1]/l[1]/normalize-space(.)"
            as="xs:string"/>
        <xsl:variable name="authorName"
            select="ancestor::TEI/descendant::author[last()]" as="xs:string"/>
        <xsl:variable name="authorGender" select="'ND'"/>
        <xsl:variable name="date" select="'ND'"/>
        <xsl:variable name="rhyme" select="ancestor::l/@rhyme" as="xs:string"/>
        <xsl:variable name="echo" select="following::w[ancestor::l[@rhyme eq $rhyme]][1]"
            as="xs:string?"/>
        <xsl:variable name="rhymeSet" as="xs:string"
            select="(parent::l/preceding::l[@rhyme eq $rhyme]/w | parent::l/following::l[@rhyme eq $rhyme]/w) => string-join(', ')"/>
        <xsl:variable name="lineN" select="parent::l/@n"
            as="xs:string"/>
        <xsl:variable name="stanzaN" select="count(parent::l/parent::lg/preceding-sibling::lg) + 1"/>        
        <xsl:variable name="values"
            select="$id, $fileName, $incipit, $authorId, $authorName, $authorGender, $date, $lineN, string($stanzaN), normalize-space($text), current(), if(exists($echo)) then $echo else ' ', $rhymeSet"
            as="xs:string+"/>
        <xsl:value-of select="string-join($values, $del) || '&#9;cssdo&#10;'"/>
    </xsl:template>
    <xsl:template match="lg" mode="text">
        <xsl:apply-templates select="l" mode="text"/>
        <xsl:if test="following-sibling::lg">###</xsl:if>
    </xsl:template>
    <xsl:template match="l" mode="text">
        <xsl:value-of select="."/>
        <xsl:if test="following-sibling::l">~~~</xsl:if>
    </xsl:template>
</xsl:stylesheet>
