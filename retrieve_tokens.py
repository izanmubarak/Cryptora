def get_token(service):
    with open("tokens.txt") as f:
        tokens = {}
        for line in f:
            line = line.strip()
            if "=" in line:
                key, value = line.split("=", 1)
                tokens[key] = value

    match service:
        case "cmc":
            return tokens.get("CMC_TOKEN", "")
        case "bot":
            return tokens.get("BOT_TOKEN", "")
        case "mistral":
            return tokens.get("MISTRAL_TOKEN", "")
        case "fmp":
            return tokens.get("FMP_TOKEN", "")
        case _:
            return ""
