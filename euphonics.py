from conllu import parse_incr, TokenList

# splits all euphonized tokens found in a CoNLL-U file
# and modifies each syntactic tree accordingly
def euphonics(input_file, output_file):
    
    for sentence in parse_incr(input_file):
        new_sentence = TokenList() # TokenList used to form new modified sentence
        increase_id = 0            # used for increasing ids in case we add lines for euphonics
        change = {}                # dict to keep track of necessary "head" changes to be performed
        
        for token in sentence:
            flag = 0 # flag for when we encounter a euphonic

            # increase token's id value if necessary
            if increase_id > 0:
                # keep track of id changes made to modify "head" values accordingly
                change[token["id"]] = token["id"] + increase_id
                token["id"] += increase_id
                
            # check if "misc" contains euphonics information
            misc = token["misc"]
            if misc != None and "MSeg" in misc and "MGloss" in misc:
                flag = 1                                     # set euphonics flag to 1
                euphonic_first = 0                           # set to 1 if euphonic is prefixed e.g. "γι-άλλοι"
                MSeg1, MSeg2 = misc["MSeg"].split("-")       # get info from misc collumn
                MGloss1, MGloss2 = misc["MGloss"].split("-")

                # print error if "euphonic" keyword not found
                if "euphonic" not in {MGloss1, MGloss2}:
                    print("Incorrect Annotation @", sentence.metadata["text"])
                    flag = 0

                # check if euphonic is prefixed or postfixed
                if MGloss1 == "euphonic":
                    euphonic_first = 1
                    change[token["id"]] = token["id"] + 1
                    word = MSeg2
                    euph = Mseg1
                elif MGloss2 == "euphonic":
                    euphonic_first = 0
                    word = MSeg1
                    euph = MSeg2

                # original token, e.g. "γιάλλοι", "μαςε", has double id, e.g 3-4
                original = {
                    "id": (token["id"], "-", token["id"] + 1),
                    "form": token["form"],
                    "lemma": "_",
                    "upos": "_",
                    "xpos": "_",
                    "feats": "_",
                    "head": "_",
                    "deprel": "_",
                    "deps": "_",
                    "misc": token["misc"],
                }

                # token of word without euphonic, e.g. "άλλοι", "μας"             
                rest = {
                    "id": token["id"] + euphonic_first,
                    "form": word,
                    "lemma": token["lemma"],
                    "upos": token["upos"],
                    "xpos": token["xpos"],
                    "feats": token["feats"],
                    "head": token["head"],
                    "deprel": token["deprel"],
                    "deps": token["deps"],
                    "misc": token["misc"],
                }

                # token representing euphonic
                euphonic = {
                    "id": token["id"] + 1 - euphonic_first,
                    "form": euph,
                    "lemma": "_",
                    "upos": "_",
                    "xpos": "EUPH",
                    "feats": "_",
                    "head": token["id"] + euphonic_first,
                    "deprel": "euph",
                    "deps": "_",
                    "misc": "_",
                }

                # increase_id appropriately for all following tokens since we added an extra token
                increase_id += 1

            # if euphonic is found, add appropriate split tokens, else add original token
            if flag == 0:
                new_sentence.append(token)
            else:
                if euphonic_first:
                    new_sentence.append(original)
                    new_sentence.append(euphonic)
                    new_sentence.append(rest)
                else:
                    new_sentence.append(original)
                    new_sentence.append(rest)
                    new_sentence.append(euphonic)

        # apply necessary changes to the heads of each token
        for i in range(len(new_sentence)):
            if new_sentence[i]["head"] in change and new_sentence[i]["xpos"] != "EUPH":
                new_sentence[i]["head"] = change[new_sentence[i]["head"]]

        # copy over original metadata
        new_sentence.metadata = sentence.metadata
        
        # append new altered sentence to desired output file
        with open(output_file, "a") as file:
            file.write(new_sentence.serialize())
