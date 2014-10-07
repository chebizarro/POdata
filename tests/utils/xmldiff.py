import difflib
from lxml.etree import parse, XSLT, tostring, XMLParser, fromstring


xslt = """
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform"> 
<xsl:template match="node()|@*"> 
    <xsl:copy> 
        <xsl:apply-templates select="node()|@*"> 
			<xsl:sort select="name(node())" />
			<xsl:sort select="@Name" />
        </xsl:apply-templates> 
    </xsl:copy> 
</xsl:template> 
</xsl:stylesheet>
	"""

def diff_xml(fromFile, toFile, outputFile) :
	global xslt
	xml = []
	files = []

	parser = XMLParser(remove_blank_text=True)
	xslt = fromstring(xslt)
	transform = XSLT(xslt)
	
	xml.append(parse(fromFile, parser))
	xml.append(parse(toFile, parser))

	for xfile in xml :
		files.append(tostring(transform(xfile))
			.replace(" ","\n")
			.replace("><",">\n<")
			.replace("/>","\n/>")
			.replace("\">","\"\n>"))

	for nfile in files :
		index = 0
		tab = "\t"
		newfile = ""
		for line in nfile.splitlines(1) :
			if line.startswith("</") :
				index -= 1
			newfile += (tab * index) + line
			if line.startswith("</") :
				index -= 1
			if line.startswith("<") :
				index += 1
			if line.endswith("/>\n") :
				index -= 1
		nfile = newfile
	
	diff = difflib.unified_diff(
		files[0].splitlines(1),
		files[1].splitlines(1))

	if outputFile :
		with open(outputFile, "wb") as f:
			for d in diff:
				f.write(d)

