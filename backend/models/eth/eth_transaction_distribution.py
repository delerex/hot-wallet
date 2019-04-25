from typing import List

from models.eth.transaction_intent import TransactionIntent
from models.eth.output_wallet import OutputWallet
from models.eth.input_wallet import InputWallet


class EthTransactionDistribution:
    @staticmethod
    def _get_total_balance(wallets: List[InputWallet]) -> int:
        return sum([w.balance for w in wallets])

    def get_transaction_intents(self, wallets: List[InputWallet], outs_percent: list) -> List[TransactionIntent]:
        total = self._get_total_balance(wallets)
        out_amounts = [OutputWallet(addr, int(total * percent / 100)) for (addr, percent) in outs_percent]
        txs = []
        j = 0
        for in_wallet in wallets:
            balance = in_wallet.balance
            while balance > 0:
                out_wallet = out_amounts[j]
                if balance >= out_wallet.amount:
                    tx_amount = out_wallet.amount
                    balance -= tx_amount
                    out_amounts[j] = OutputWallet(out_wallet.addr, 0)
                    j += 1
                else:
                    tx_amount = balance
                    out_amounts[j] = OutputWallet(out_wallet.addr, out_wallet.amount - balance)
                    balance = 0
                txs.append(TransactionIntent(
                    in_wallet=in_wallet,
                    out_address=out_wallet.addr,
                    amount=tx_amount
                ))
                if j >= len(out_amounts):
                    break

        return txs
