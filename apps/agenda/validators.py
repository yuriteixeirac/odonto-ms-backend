def validate_cpf(cpf: str) -> bool:
    # Remove caracteres não numéricos
    cpf = "".join(filter(str.isdigit, cpf))

    # Verifica se tem 11 dígitos ou se todos são iguais
    if len(cpf) != 11 or len(set(cpf)) == 1:
        return False

    # Validação do primeiro dígito
    sum_val = sum(int(cpf[i]) * (10 - i) for i in range(9))
    digit_1 = (sum_val * 10) % 11
    if digit_1 == 10:
        digit_1 = 0

    if digit_1 != int(cpf[9]):
        return False

    # Validação do segundo dígito
    sum_val = sum(int(cpf[i]) * (11 - i) for i in range(10))
    digit_2 = (sum_val * 10) % 11
    if digit_2 == 10:
        digit_2 = 0

    return digit_2 == int(cpf[10])
