from beembase.signedtransactions import Signed_Transaction
from beemgraphenebase.base58 import Base58
from beemgraphenebase.account import PublicKey

def get_signer(trx):
    try:
        st = Signed_Transaction(trx.copy())
    except Exception:
        return None

    keys = []
    for key in st.verify(recover_parameter=True):
        keys.append(format(Base58(key, prefix='STM'), 'STM'))
    return keys
