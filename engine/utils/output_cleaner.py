def clean_output(text: str) -> str:
    sections = ["ANALYSIS", "SOLUTION", "IMPLEMENTATION", "IMPROVEMENTS"]
    result = []

    for section in sections:
        start = text.find(section)

        if start == -1:
            continue

        end = len(text)

        for next_section in sections:
            pos = text.find(next_section, start +1)

            if pos != -1:
                end = min(end, pos)

        result.append(text[start:end].strip())

    return "\n\n".join(result)