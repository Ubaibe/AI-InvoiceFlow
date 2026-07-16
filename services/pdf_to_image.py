import pypdfium2


def pdf_first_page(pdf_path):

    pdf = pypdfium2.PdfDocument(pdf_path)

    page = pdf[0]

    bitmap = page.render(scale=2)

    pil = bitmap.to_pil()

    image_path = pdf_path + ".png"

    pil.save(image_path)

    return image_path