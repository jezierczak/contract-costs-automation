# from pathlib import Path
# from lxml import etree
#
#
# def render_xml_to_pdf(
#     *,
#     xml_path: Path,
#     xslt_path: Path,
#     output_pdf: Path,
# ) -> None:
#
#     xml = etree.parse(str(xml_path))
#     xslt = etree.parse(str(xslt_path))
#
#     transform = etree.XSLT(xslt)
#
#     html = transform(xml)
#
#     HTML(string=str(html)).write_pdf(str(output_pdf))