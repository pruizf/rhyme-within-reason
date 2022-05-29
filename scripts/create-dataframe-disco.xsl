<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:xs="http://www.w3.org/2001/XMLSchema" exclude-result-prefixes="xs"
    xpath-default-namespace="http://www.tei-c.org/ns/1.0" version="3.0">
    <xsl:output method="text"/>
    <xsl:variable name="text">
        <xsl:apply-templates mode="text" select="//lg"/>
    </xsl:variable>
    <xsl:template match="/">
        <xsl:variable name="fileName" select="base-uri(.) => replace('.xml', '.txt') => substring-after('disco/')"/>
        <xsl:result-document href="{$fileName}">
            <xsl:apply-templates select="//w"/>
        </xsl:result-document>
    </xsl:template>
    <xsl:template match="w">
        <xsl:variable name="del" as="xs:string" select="'&#9;'"/>
        <xsl:variable name="id" select="generate-id(.)" as="xs:string"/>
        <xsl:variable name="sonnet" select="ancestor::lg[@type eq 'sonnet']" as="node()"/>
        <xsl:variable name="sonnetId" select="$sonnet/@xml:id" as="xs:string"/>
        <xsl:variable name="incipit" select="($sonnet/descendant::l)[1]/normalize-space(.)"
            as="xs:string"/>
        <xsl:variable name="author" select="ancestor::TEI/descendant::person" as="node()"/>
        <xsl:variable name="authorId" select="$author/@xml:id" as="xs:string"/>
        <xsl:variable name="authorName"
            select="$author/persName[@type eq 'source']/normalize-space(.)" as="xs:string"/>
        <xsl:variable name="authorGender" select="$author/sex/@content" as="xs:string"/>
        <xsl:variable name="date" select="$author/death/date[@type eq 'century']" as="xs:string"/>
        <xsl:variable name="rhyme" select="ancestor::l/@rhyme" as="xs:string"/>
        <xsl:variable name="echo" select="following::w[ancestor::l[@rhyme eq $rhyme]][1]"
            as="xs:string?"/>
        <xsl:variable name="rhymeSet" as="xs:string"
            select="(parent::l/preceding::l[@rhyme eq $rhyme]/w | parent::l/following::l[@rhyme eq $rhyme]/w) => string-join(', ')"/>
        <xsl:variable name="lineN" select="string(count(parent::l/preceding-sibling::l) + 1)"
            as="xs:string"/>
        <xsl:variable name="stanzaN" select="parent::l/parent::lg/@n" as="xs:string"/>        
        <xsl:variable name="values"
            select="$id, $sonnetId, $incipit, $authorId, $authorName, $authorGender, $date, $lineN, $stanzaN, normalize-space($text), current(), $echo, $rhymeSet"
            as="xs:string+"/>
        <xsl:value-of select="string-join($values, $del) || '&#10;'"/>
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
