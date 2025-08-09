
import cv2
import numpy as np
import pytesseract

def process_form_image(image_path):
    img = cv2.imread(image_path)
    if img is None:
        return "Erro: Não foi possível carregar a imagem."

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    adjusted = cv2.convertScaleAbs(gray, alpha=1.5, beta=0)
    thresh = cv2.adaptiveThreshold(adjusted, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2)

    product_data = []

    # Definir as regiões de interesse (ROIs) para os códigos de produto e as caixas de escolha
    # Estas coordenadas são aproximadas e baseadas na imagem 'image.png' fornecida.
    # Elas podem precisar de ajuste fino se o formulário mudar de tamanho ou posição.

    # Para a primeira tabela (esquerda)
    # Coordenadas (y_start, y_end, x_code_start, x_code_end, x_choice_start, x_choice_end)
    table1_rows_info = [
        (60, 85, 15, 100, 260, 290), # Linha 1
        (85, 110, 15, 100, 260, 290), # Linha 2
        (110, 135, 15, 100, 260, 290), # Linha 3
        (135, 160, 15, 100, 260, 290), # Linha 4
        (160, 185, 15, 100, 260, 290), # Linha 5
        (185, 210, 15, 100, 260, 290), # Linha 6
        (210, 235, 15, 100, 260, 290), # Linha 7
    ]

    # Para a segunda tabela (direita)
    # As coordenadas X serão deslocadas para a direita
    table2_rows_info = [
        (60, 85, 365, 450, 610, 640), # Linha 1
        (85, 110, 365, 450, 610, 640), # Linha 2
        (110, 135, 365, 450, 610, 640), # Linha 3
        (135, 160, 365, 450, 610, 640), # Linha 4
        (160, 185, 365, 450, 610, 640), # Linha 5
        (185, 210, 365, 450, 610, 640), # Linha 6
        (210, 235, 365, 450, 610, 640), # Linha 7
    ]

    all_rows_info = table1_rows_info + table2_rows_info

    for y_start, y_end, x_code_start, x_code_end, x_choice_start, x_choice_end in all_rows_info:
        # Extrair código do produto
        code_roi = gray[y_start:y_end, x_code_start:x_code_end]
        extracted_code = pytesseract.image_to_string(code_roi, config="--psm 7 --oem 3").strip()
        product_code = "".join(filter(str.isdigit, extracted_code)) # Apenas dígitos

        # Extrair marcação da coluna 'Escolha'
        choice_roi = thresh[y_start:y_end, x_choice_start:x_choice_end]
        
        black_pixel_count = np.sum(choice_roi == 255)
        total_pixels = choice_roi.shape[0] * choice_roi.shape[1]
        
        quantity = 0
        if total_pixels > 0:
            black_pixel_percentage = (black_pixel_count / total_pixels) * 100
            
            # Se a porcentagem de pixels pretos for maior que um limiar, consideramos marcado
            # Um 'X' terá uma porcentagem menor que um quadrado totalmente preenchido
            if black_pixel_percentage > 5: # Limiar ajustado para ser mais sensível a 'X' e preenchimento
                quantity = 1 # Assumindo quantidade 1 para marcado

        if product_code and quantity > 0:
            product_data.append(f"{product_code},{quantity}")

    output_lines = []
    if product_data:
        output_lines.append("Código_Produto,Quantidade")
        output_lines.extend(product_data)
    else:
        output_lines.append("Nenhum produto ou marcação detectada.")

    return "\n".join(output_lines)

if __name__ == '__main__':
    image_path = 'image.png'
    output = process_form_image(image_path)
    print(output)


