def check_answer(answer):
    breaking_points = ['.', '(', '-']
    for breaking_point in breaking_points:
        if breaking_point in answer:
            answer = answer[:answer.find(breaking_point)]
    return answer