# from pathlib import Path
#
# from contract_costs.ksef.render.xml_to_pdf import render_xml_to_pdf
#
#
# class XmlPreviewRendererService:
#
#     @staticmethod
#     def render( *, xml_path: Path) -> Path:
#
#         pdf_path = xml_path.with_name(xml_path.stem + "_preview.pdf")
#
#         render_xml_to_pdf(
#             xml_path=xml_path,
#             xslt_path=Path("resources/ksef/fa3_visualisation.xslt"),
#             output_pdf=pdf_path,
#         )
#
#         return pdf_path