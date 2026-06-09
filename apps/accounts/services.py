import requests


class CEPService:
    api = "https://brasilapi.com.br/api/cep/v1/"

    @staticmethod
    def get_endereco(cep: str) -> dict[str, str]:
        response = requests.get(f"{CEPService.api}/{cep}")

        if response.status_code == 404:
            raise ValueError("CEP digitado não encontrou nenhum endereço.")

        endereco = response.json()

        return {
            "estado": endereco["state"],
            "cidade": endereco["city"],
            "bairro": endereco["neighborhood"],
            "rua": endereco["street"],
        }
