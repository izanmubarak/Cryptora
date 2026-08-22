def get_token(service):
    with open("tokens.txt") as f:
        tokens = {}
        for line in f:
            line = line.strip()
            if "=" in line:
                key, value = line.split("=", 1)
                tokens[key] = value

    if service is True or service == "cmc":
        return tokens.get("CMC_TOKEN", "")

    if service is False or service == "bot":
        return tokens.get("BOT_TOKEN", "")

    if service == "coindesk":
        return tokens.get("COINDESK_TOKEN", "")

    if service == "mistral":
        return tokens.get("MISTRAL_TOKEN", "")

    return ""
