import firecloud.api as FAPI


def whoami(fapi=FAPI):
    """Wrapper for whoami"""
    return fapi.whoami()
