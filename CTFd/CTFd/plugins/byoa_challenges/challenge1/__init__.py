# from .. import ByoaChallengeDeploys


def validate_chalenge(bcd):
    # TODO Bhavik to fill in validation code
    tf_data = bcd.get_terraform_state_dict()
    return tf_data

    #example bad return
    return {"validate_result": False, "errors": ["could not validate"]}
    #example good return
    return {"validate_result": False, "flag": "thisistheflag"}
