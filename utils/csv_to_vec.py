def csv_to_vec(csv, cv, tfidf):
    feature_names = cv.get_feature_names_out()
    top_n = 100
    vec = tfidf.transform(cv.transform([csv]))

    #changing matrix' format to transactional and sort the values
    vec_COO = vec.tocoo()
    sorted_vec = sorted(zip(vec_COO.col, vec_COO.data), key=lambda x: (x[1], x[0]), reverse=True)

    #extracting top_n values from the vector
    sorted_vec = sorted_vec[:top_n]

    scores = []
    features = []

    for i, score in sorted_vec:
        scores.append(round(score, 3))
        features.append(feature_names[i])
    
    final = {}
    
    for i, val in enumerate(features):
        final[features[i]] = scores[i]
    
    return final


