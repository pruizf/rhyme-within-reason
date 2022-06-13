<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns="http://www.tei-c.org/ns/1.0"
    xmlns:functx="http://www.functx.com" xpath-default-namespace="http://www.tei-c.org/ns/1.0"
    exclude-result-prefixes="#all" version="3.0">
    <xsl:mode on-no-match="shallow-copy"/>
    <xsl:output method="xml" indent="yes"></xsl:output>
    <xsl:function name="functx:escape-for-regex" as="xs:string">
        <xsl:param name="arg" as="xs:string?"/>

        <xsl:sequence select="
                replace($arg,
                '(\.|\[|\]|\\|\||\-|\^|\$|\?|\*|\+|\{|\}|\(|\))', '\\$1')
                "/>

    </xsl:function>
    <xsl:function name="functx:substring-after-last" as="xs:string">
        <xsl:param name="arg" as="xs:string?"/>
        <xsl:param name="delim" as="xs:string"/>
        <xsl:sequence select="
                replace($arg, concat('^.*', functx:escape-for-regex($delim)), '')
                "/>
    </xsl:function>
    <xsl:variable name="author" select="base-uri(.) => substring-after('source_with_rhymes/') => substring-before('_') => replace('([A-Z])', ' $1')"/>
    <xsl:template match="titleStmt">
        <titleStmt>
            <title><xsl:value-of select="ancestor::TEI/descendant::body/normalize-space(descendant::title)"/></title>
            <author><xsl:value-of select="$author"/></author>
            <xsl:copy-of select="respStmt"/>
            <respStmt>
                <name xml:id="prf">Pablo Ruiz Fabo</name>
                <resp>Rhyme annotation</resp>
            </respStmt>            
            <respStmt>
                <name xml:id="heb">Helena Bermúdez Sabel</name>
                <resp>Encoding review</resp>
            </respStmt>
        </titleStmt>
    </xsl:template>
    <xsl:template match="encodingDesc">
        <xsl:copy-of select="current()"/>
        <revisionDesc>
            <change who="#heb" when="2022-06-11">Retrieved files from <ptr target="https://github.com/bncolorado/CorpusSonetosSigloDeOro"/></change>            
            <change who="#prf" when="2022-06-11">Added rhyme annotation using <ref target="https://github.com/versotym/rhymeTagger">rhymetagger</ref></change>            
            <change who="#heb" when="2022-06-11">Added rhyme word and title/author metadata</change>
        </revisionDesc>
    </xsl:template>
    <xsl:template match="l">
        <l>
            <xsl:copy-of select="@*"/>
            <xsl:choose>
                <xsl:when test="@rhyme ne '-'">
                    <xsl:variable name="tokens" select="tokenize(., '[\s]+')"/>
                    <xsl:for-each select="1 to count($tokens)">
                        <xsl:choose>
                            <xsl:when test="current() ne count($tokens)">
                                <xsl:value-of select="concat($tokens[current()], ' ')"/>
                            </xsl:when>
                            <xsl:otherwise>
                                <xsl:analyze-string select="$tokens[current()]"
                                    regex='[^.,\?!;«»¡¿\-\(\)\]\[\*–:"“”…]+'>
                                    <xsl:matching-substring>
                                        <w type="rhyme"><xsl:value-of select="."/></w>
                                    </xsl:matching-substring>
                                    <xsl:non-matching-substring>
                                        <xsl:value-of select="."/>
                                    </xsl:non-matching-substring>
                                </xsl:analyze-string>
                            </xsl:otherwise>
                        </xsl:choose>
                    </xsl:for-each>
                </xsl:when>
                <xsl:otherwise>
                    <xsl:apply-templates/>
                </xsl:otherwise>
            </xsl:choose>
        </l>

    </xsl:template>

</xsl:stylesheet>
