import base64
import io
from datetime import datetime
from typing import Dict
from PIL import Image, ImageDraw, ImageFont, ImageOps
import qrcode

class ReceiptGenerator:
    def __init__(self):
        self.width = 614
        self.height = 1280
        self.bg_color = "#FFFFFF"
        self.header_green = "#35B047"
        self.gray = "#757575"
        self.green = "#32B46E"
        self.light_gray = "#F6F6F6"
        self.border_gray = "#E6E6E6"
        self.text_color = "#222222"
        self.badge_green = "#36B169"
        self.box_green = "#2C9A55"

    def generate_receipt(self, payment_data: Dict) -> bytes:
        """Genera el recibo como imagen PNG siguiendo el diseño exacto"""
        # Configure locale in spanish for dates
        import locale
        try:
            locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')
        except:
            try:
                locale.setlocale(locale.LC_TIME, 'Spanish_Spain.1252')
            except:
                pass  
        
        img = Image.new('RGB', (self.width, self.height), self.bg_color)
        draw = ImageDraw.Draw(img)

        # Roboto Fonts
        try:
            title_font = ImageFont.truetype("/usr/share/fonts/truetype/roboto/unhinted/RobotoTTF/Roboto-Bold.ttf", 26)
            header_font = ImageFont.truetype("/usr/share/fonts/truetype/roboto/unhinted/RobotoTTF/Roboto-Bold.ttf", 17)
            normal_font = ImageFont.truetype("/usr/share/fonts/truetype/roboto/unhinted/RobotoTTF/Roboto-Regular.ttf", 16)
            small_font = ImageFont.truetype("/usr/share/fonts/truetype/roboto/unhinted/RobotoTTF/Roboto-Regular.ttf", 14)
            tiny_font = ImageFont.truetype("/usr/share/fonts/truetype/roboto/unhinted/RobotoTTF/Roboto-Regular.ttf", 13)
        except:
            title_font = header_font = normal_font = small_font = tiny_font = ImageFont.load_default()

        y_pos = 0

        # 1. GREEN HEADER WITH ROUNDED CORNERS
        # Create green header with rounded corners only at the top
        header_height = 135
        draw.rounded_rectangle([0, 0, self.width, header_height], radius=35, fill=self.header_green)
        
        # Logo circular blanco con Y
        logo_size = 70
        logo_x, logo_y = 30, 25
        draw.ellipse([logo_x, logo_y, logo_x + logo_size, logo_y + logo_size], fill="white")
        
        # Letter Y centered in the circle
        y_text_x = logo_x + (logo_size // 2) - 12
        y_text_y = logo_y + (logo_size // 2) - 18
        self._draw_center_text(draw, "Y", y_text_y, self.width, title_font, self.header_green)
        
        # Textos del header
        self._draw_center_text(draw, "YnterX App", 48, self.width, title_font, "white")
        self._draw_center_text(draw, "Finance Solutions", 78, self.width, normal_font, "white")

        y_pos = 153

        # 2. CENTERED TITLE
        self._draw_center_text(draw, "Recibo de Pago", y_pos, self.width, title_font, self.text_color)
        y_pos += 36
        
        # Centered receipt number
        receipt_number = payment_data['client_data']['receiptNumber']
        self._draw_center_text(draw, f"No. {receipt_number}", y_pos, self.width, normal_font, self.gray)
        y_pos += 32

        # Divider line
        line_margin = 30
        draw.line([line_margin, y_pos + 14, self.width - line_margin, y_pos + 14], fill=self.border_gray, width=2)
        y_pos += 36

        # 3. CLIENT INFORMATION
        draw.text((38, y_pos), "Informacion del Cliente", fill=self.text_color, font=header_font)
        y_pos += 28
        
        cl = payment_data['client_data']
        client_info = [
            ("Cliente:", cl['clientName']), 
            ("Cédula:", cl['clientId']), 
            ("Contrato:", cl['contractNumber'])
        ]
        
        for label, value in client_info:
            draw.text((38, y_pos), label, fill=self.gray, font=normal_font)
            # Align values to the right of the available area
            value_x = self.width - 38 - self._get_text_width(draw, value, normal_font)
            draw.text((value_x, y_pos), value, fill=self.text_color, font=normal_font)
            y_pos += 26
        
        y_pos += 18

        # 4. PAYMENT INFORMATION
        draw.text((38, y_pos), "Informacion del Pago", fill=self.text_color, font=header_font)
        y_pos += 28
        
        
        payment_date = datetime.fromisoformat(payment_data['payment_date'].replace('Z', '+00:00'))
        formatted_date = payment_date.strftime("%d %B %Y, %I:%M %p").replace('AM', 'a.m.').replace('PM', 'p.m.')
        
        # Generar referencia si no existe
        payment_ref = payment_data.get('payment_reference', f"TRF-{payment_date.strftime('%Y%m%d%H%M')}")
        
        payment_info = [
            ("Fecha:", formatted_date), 
            ("Método:", payment_data['payment_method']), 
            ("Referencia:", payment_ref)
        ]
        
        for label, value in payment_info:
            draw.text((38, y_pos), label, fill=self.gray, font=normal_font)
            value_x = self.width - 38 - self._get_text_width(draw, value, normal_font)
            draw.text((value_x, y_pos), value, fill=self.text_color, font=normal_font)
            y_pos += 24

        # Badge of State "PAGADO"
        draw.text((38, y_pos), "Estado:", fill=self.gray, font=normal_font)
        badge_text = "PAGADO"
        badge_width = 80
        badge_height = 27
        badge_x = self.width - 38 - badge_width
        draw.rounded_rectangle([badge_x, y_pos - 4, badge_x + badge_width, y_pos + badge_height - 4], 
                             radius=12, fill=self.badge_green)
        
        # Centrar texto en el badge
        badge_text_x = badge_x + (badge_width - self._get_text_width(draw, badge_text, tiny_font)) // 2
        draw.text((badge_text_x, y_pos + 3), badge_text, fill="white", font=tiny_font)
        y_pos += 40

        # 5. TABLA DE CUOTAS PAGADAS
        draw.text((38, y_pos), "Cuotas Pagadas", fill=self.text_color, font=header_font)
        y_pos += 26
        
        # Calculate table height
        paid_items = [item for item in payment_data['payment_items'] if item['paid_amount'] > 0]
        table_top = y_pos
        table_header_height = 37
        table_row_height = 33
        table_height = table_header_height + (len(paid_items) * table_row_height)
        
        # Fondo de la tabla con bordes redondeados
        table_margin = 30
        draw.rounded_rectangle([table_margin, table_top, self.width - table_margin, table_top + table_height], 
                             radius=12, fill=self.light_gray)
        
        # Table headers
        headers = ["CUOTA", "FECHA VENC.", "MONTO"]
        header_positions = [52, 238, 500]
        
        for i, header in enumerate(headers):
            draw.text((header_positions[i], table_top + 12), header, fill=self.gray, font=small_font)
        
        # Gray separator line below table header
        draw.line([table_margin, table_top + table_header_height - 1, self.width - table_margin, table_top + table_header_height - 1], fill=self.border_gray, width=1)
        y_pos += 10
        
        # Data rows
        y_row = table_top + table_header_height
        for item in paid_items:
            due_date = datetime.fromisoformat(item['due_date']).strftime("%d/%m/%Y")
            
            draw.text((header_positions[0], y_row + 6), f"#{item['payment_number']}", fill=self.text_color, font=normal_font)
            draw.text((header_positions[1], y_row + 6), due_date, fill=self.text_color, font=normal_font)
            
            # Monto en verde, alineado a la derecha de su columna
            amount_text = f"${float(item['paid_amount']):,.2f}"
            amount_width = self._get_text_width(draw, amount_text, normal_font)
            amount_x = self.width - table_margin - 30 - amount_width
            draw.text((amount_x, y_row + 6), amount_text, fill=self.green, font=normal_font)
            
            y_row += table_row_height
        
        y_pos = table_top + table_height + 22
        y_pos += 10

        # 6. GREEN BOX WITH ROUNDED CORNERS
        totals_margin = 24
        totals_height = 120
        draw.rounded_rectangle([totals_margin, y_pos, self.width - totals_margin, y_pos + totals_height], 
                             radius=18, fill=self.box_green)
        
        # Total texts
        subtotal_text = f"${float(payment_data['sub_total']):,.2f}"
        discount_text = f"-${float(payment_data['discount']):,.2f}"
        total_text = f"${float(payment_data['total_paid']):,.2f}"
        
        # Subtotal
        draw.text((48, y_pos + 16), "Subtotal:", fill="white", font=normal_font)
        subtotal_x = self.width - totals_margin - 30 - self._get_text_width(draw, subtotal_text, normal_font)
        draw.text((subtotal_x, y_pos + 16), subtotal_text, fill="white", font=normal_font)
        
        # Discount
        draw.text((48, y_pos + 39), "Descuento:", fill="white", font=normal_font)
        discount_x = self.width - totals_margin - 30 - self._get_text_width(draw, discount_text, normal_font)
        draw.text((discount_x, y_pos + 39), discount_text, fill="white", font=normal_font)
        
        y_pos += 10
        # White separator line below Discount
        draw.line([48, y_pos + 55, self.width - 48, y_pos + 55], fill="white", width=1)
        
        # Total Paid
        draw.text((48, y_pos + 72), "Total Pagado:", fill="white", font=header_font)
        total_x = self.width - totals_margin - 30 - self._get_text_width(draw, total_text, header_font)
        draw.text((total_x, y_pos + 72), total_text, fill="white", font=header_font)
        
        y_pos += totals_height + 24

        # 7. CONTRACT BALANCE
        draw.text((38, y_pos), "Balance del Contrato", fill=self.text_color, font=header_font)
        y_pos += 28
        
        # Calculate previous balance
        previous_balance = float(payment_data['remaining_balance']) + float(payment_data['total_applied'])
        
        # Previous Balance
        draw.text((38, y_pos), "Balance Anterior:", fill=self.gray, font=normal_font)
        value_x = self.width - 38 - self._get_text_width(draw, f"${previous_balance:,.2f}", normal_font)
        draw.text((value_x, y_pos), f"${previous_balance:,.2f}", fill=self.gray, font=normal_font)
        y_pos += 26
        
        # Applied Payment
        draw.text((38, y_pos), "Pago Aplicado:", fill=self.gray, font=normal_font)
        value_x = self.width - 38 - self._get_text_width(draw, f"-${float(payment_data['total_applied']):,.2f}", normal_font)
        draw.text((value_x, y_pos), f"-${float(payment_data['total_applied']):,.2f}", fill=self.gray, font=normal_font)
        y_pos += 26
        
        # Green separator line between Applied Payment and New Balance
        draw.line([38, y_pos, self.width - 38, y_pos], fill=self.header_green, width=2)
        y_pos += 15
        
        # New Balance
        draw.text((38, y_pos), "Nuevo Balance:", fill=self.text_color, font=header_font)
        value_x = self.width - 38 - self._get_text_width(draw, f"${float(payment_data['remaining_balance']):,.2f}", header_font)
        draw.text((value_x, y_pos), f"${float(payment_data['remaining_balance']):,.2f}", fill=self.green, font=header_font)
        y_pos += 68

        # 8. CENTERED THANK YOU MESSAGE
        self._draw_center_text(draw, "¡Gracias por su pago!", y_pos, self.width, header_font, self.text_color)
        y_pos += 32

        # 9. CENTERED QR CODE
        qr_img = self._generate_qr_code(payment_data['client_data']['contractNumber'])
        qr_size = 120
        qr_x = (self.width - qr_size) // 2
        img.paste(qr_img, (qr_x, y_pos))
        y_pos += qr_size + 20

        # 10. CENTERED FOOTER
        footer_lines = [
            "YnterX App · Finance Solutions",
            "📧 info@ynterx.com    📞 +1 (809) 123-4567",
            "www.ynterx.com"
        ]
        
        for line in footer_lines:
            self._draw_center_text(draw, line, y_pos, self.width, tiny_font, self.gray)
            y_pos += 20

        return self._image_to_bytes(img)

    def _get_text_width(self, draw, text, font):
        """Obtiene el ancho del texto de manera compatible con diferentes versiones de PIL"""
        try:
            # Modern PIL version
            bbox = draw.textbbox((0, 0), text, font=font)
            return bbox[2] - bbox[0]
        except AttributeError:
            # Old PIL version
            try:
                return draw.textlength(text, font=font)
            except AttributeError:
                # Fallback for very old versions
                return draw.textsize(text, font=font)[0]

    def _draw_center_text(self, draw, text, y, width, font, color):
        """Dibuja texto centrado horizontalmente"""
        text_width = self._get_text_width(draw, text, font)
        x = (width - text_width) // 2
        draw.text((x, y), text, fill=color, font=font)

    def _generate_qr_code(self, contract_number: str) -> Image.Image:
        """Genera código QR con el estilo exacto de la imagen"""
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=5,
            border=1
        )
        qr.add_data(f"https://ynterx.com/contract/{contract_number}")
        qr.make(fit=True)
        
        # Crear imagen QR
        qr_img = qr.make_image(fill_color="black", back_color="white").convert("RGB")
        
        # Agregar borde blanco
        qr_img = ImageOps.expand(qr_img, border=4, fill='white')
        
        # Resize to exact size
        return qr_img.resize((120, 120), Image.Resampling.LANCZOS)

    def _image_to_bytes(self, img: Image.Image) -> bytes:
        """Convierte imagen PIL a bytes"""
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='PNG', quality=95, optimize=True)
        return img_byte_arr.getvalue()

    def image_to_base64(self, img_bytes: bytes) -> str:
        """Convierte bytes de imagen a base64 para retorno"""
        return f"data:image/png;base64,{base64.b64encode(img_bytes).decode()}"

    def generate_receipt_id(self) -> str:
        """Genera un ID único para el recibo"""
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        return f"RCP-{timestamp}"