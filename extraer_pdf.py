from PyPDF2 import PdfReader
import os

# Carpeta donde están los PDFs
pdf_folder = r"C:\Users\ramir\Proyecto-Alura-antiumGear-\documentos"

# Carpeta de salida para los .txt
output_folder = r"C:\Users\ramir\Proyecto-Alura-antiumGear-\documentos_txt"
os.makedirs(output_folder, exist_ok=True)

# Lista de PDFs y nombres de salida
pdf_files = {
    "Politica_Privacidad_AntiumGear_Ltda.pdf": "Politica_Privacidad.txt",
    "Politica_Reembolsos_Devoluciones_AntiumGear.pdf": "Politica_Reembolsos.txt",
    "Terminos_Condiciones_AntiumGear.pdf": "Terminos_Condiciones.txt",
    "Guia_Envios_Directos_AntiumGear.pdf": "Guia_Envios.txt",
    "Matriz_FAQs_Master_AntiumGear.pdf": "Matriz_FAQs.txt"
}

# Procesar cada PDF
for pdf_name, txt_name in pdf_files.items():
    path = os.path.join(pdf_folder, pdf_name)
    reader = PdfReader(path)

    output_file = os.path.join(output_folder, txt_name)
    with open(output_file, "w", encoding="utf-8") as f:
        for page_num, page in enumerate(reader.pages, start=1):
            texto = page.extract_text()
            f.write(f"\n--- Página {page_num} ---\n")
            f.write(texto)

    print(f"{txt_name} creado en documentos_txt")


