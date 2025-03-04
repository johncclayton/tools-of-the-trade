from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.units import inch

from config import get_config
import os


def generate_pdf_report(grouped_data, output_filename='TradeProgressReport.pdf'):
    config = get_config()
    output_dir = config.get('paths', 'output_dir', fallback='.')
    pdf_filename = os.path.join(output_dir, output_filename)

    doc = SimpleDocTemplate(pdf_filename, pagesize=landscape(letter))
    styles = getSampleStyleSheet()
    modern_style = ParagraphStyle('Modern', parent=styles['Normal'],
                                  fontName='Helvetica', fontSize=10,
                                  leading=12, textColor=colors.black)
    no_unrealized_style = ParagraphStyle('NoUnrealized', parent=styles['Normal'],
                                         fontName='Helvetica-Bold', fontSize=36,
                                         textColor=colors.Color(0.4, 0.4, 0.4),
                                         alignment=1)
    story = []

    for year, data in sorted(grouped_data.items()):
        story.append(Paragraph(f"Year: {year}", modern_style))
        story.append(Paragraph("Realized Profit/Loss:", modern_style))

        realized_table_data = [
            ["Symbol", "DateIn", "PriceIn", "SharesIn", "DateOut", "PriceOut",
             "SharesOut", "FeesIn", "FeesOut", "Profit", "Currency"]
        ]
        for strategy, trades in data["realized"]["trades"].items():
            for trade in trades:
                realized_table_data.append([
                    trade['Symbol'], trade['DateIn'],
                    f"{trade['PriceIn']:.2f}", f"{trade['SharesIn']:.0f}",
                    trade['DateOut'], f"{trade['PriceOut']:.2f}",
                    f"{trade['SharesOut']:.0f}", f"{trade['FeesIn']:.2f}",
                    f"{trade['FeesOut']:.2f}", f"${trade['Profit']:.2f}", trade['Currency']
                ])

        col_widths = [
            1.2 * inch, 1.5 * inch, 0.8 * inch, 0.8 * inch,
            1.5 * inch, 0.8 * inch, 0.8 * inch, 0.8 * inch,
            0.8 * inch, 1.0 * inch, 0.8 * inch
        ]
        t = Table(realized_table_data, colWidths=col_widths)
        t.setStyle(TableStyle([
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("BACKGROUND", (0, 0), (-1, 0), colors.lightblue)
        ]))
        story.append(t)

        # Calculate yearly totals
        total_profit_loss = 0
        total_used_capital = 0
        for strategy in data["realized"]["profit"]:
            total_profit_loss += data["realized"]["profit"][strategy]
            total_used_capital += data["realized"]["capital"][strategy]
        total_profit_perc = (total_profit_loss / total_used_capital) * 100 if total_used_capital else 0

        # Add yearly totals table
        yearly_totals_data = [
            ["Total Profit/Loss:", f"${total_profit_loss:.2f}"],
            ["Capital Used:", f"${total_used_capital:.2f}"],
            ["Profit %:", f"{total_profit_perc:.2f}%"]
        ]
        totals_table = Table(yearly_totals_data, colWidths=[2.0 * inch, 2.0 * inch])
        totals_table.setStyle(TableStyle([
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("BACKGROUND", (0, 0), (-1, 0), colors.lightblue)
        ]))
        story.append(PageBreak())
        story.append(Paragraph(f"Year: {year}", modern_style))
        story.append(Paragraph("Year Totals:", modern_style))
        story.append(totals_table)

        story.append(PageBreak())
        story.append(Paragraph(f"Year: {year}", modern_style))
        story.append(Paragraph("Unrealized Profit/Loss and Used Capital:", modern_style))

        if not data["unrealized"]["capital"]:
            story.append(Paragraph("No Unrealized Trades Listed", no_unrealized_style))
        else:
            unrealized_table_data = [["Strategy", "Symbol", "Profit/Loss", "Cost Basis", "Profit %"]]
            for strategy, symbol_data in data["unrealized"]["capital"].items():
                for symbol, cap in symbol_data.items():
                    pf = data["unrealized"]["profit"][(strategy, symbol)]
                    pf_perc = (pf / cap) * 100 if cap else 0
                    unrealized_table_data.append([
                        strategy, symbol, f"${pf:.2f}", f"${cap:.2f}", f"{pf_perc:.2f}%"
                    ])
            col_count = len(unrealized_table_data[0])
            col_width = doc.width / col_count
            t_unreal = Table(unrealized_table_data, colWidths=[col_width] * col_count)
            t_unreal.setStyle(TableStyle([
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("BACKGROUND", (0, 0), (-1, 0), colors.lightblue)
            ]))
            story.append(t_unreal)

        story.append(PageBreak())

    doc.build(story)

    return pdf_filename
