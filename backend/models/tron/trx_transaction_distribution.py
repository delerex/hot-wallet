from typing import List, Dict

from models.tron.input_wallet import InputWallet
from models.tron.output_wallet import OutputWallet
from models.tron.transaction_intent import TransactionIntent


class TronTransactionDistribution:

    def __init__(self):
        self.transaction_points = 268
        self.create_account_fee = 100000

    def get_transaction_intents(self,
                                wallets: List[InputWallet],
                                out_wallets: List[OutputWallet]) -> List[TransactionIntent]:
        intents_without_fee = self._dispatch(wallets, out_wallets)
        total_fee = self._calculate_fee(wallets, intents_without_fee)
        intents = self._dispatch(wallets, out_wallets, total_fee)
        self._check_calculations(wallets, intents, total_fee)
        return intents

    @staticmethod
    def _get_total_balance(wallets: List[InputWallet], total_fee) -> int:
        return sum([w.balance for w in wallets]) - total_fee

    def _dispatch(self,
                  wallets: List[InputWallet],
                  out_wallets: List[OutputWallet],
                  total_fee=0) -> List[TransactionIntent]:
        # total balance - fee
        total = self._get_total_balance(wallets, total_fee)
        # print("_dispatch, total:", total, ", total_fee:", total_fee)
        # prepare amount to fill
        out_amounts = [OutputWallet(w.address,
                                    w.is_exist,
                                    w.percentage,
                                    int(total * w.percentage / 100),
                                    )
                       for w in out_wallets]
        txs = []
        j = 0
        created_wallet = set()
        for in_wallet in wallets:
            balance = in_wallet.balance
            available_bandwidth = in_wallet.available_bandwidth
            while balance > 0:
                out_wallet = out_amounts[j]

                # calculate fee
                if not out_wallet.is_exist \
                        and out_wallet.address not in created_wallet:
                    fee = self.create_account_fee
                    created_wallet.add(out_wallet.address)
                elif available_bandwidth - self.transaction_points >= 0:
                    fee = 0
                    available_bandwidth -= self.transaction_points
                else:
                    fee = self.transaction_points * 10
                # print("_dispatch: balance", balance, "out_wallet", out_wallet, "fee", fee)
                # dispatch balance
                if balance >= out_wallet.amount + fee:
                    tx_amount = out_wallet.amount
                    balance -= tx_amount + fee
                    # print("_dispatch: --> balance:", balance, "tx_amount:", tx_amount, "fee:", fee)
                    out_amounts[j] = OutputWallet(out_wallet.address,
                                                  out_wallet.is_exist,
                                                  out_wallet.percentage,
                                                  0)
                    j += 1
                else:
                    tx_amount = balance - fee
                    out_amounts[j] = OutputWallet(out_wallet.address,
                                                  out_wallet.is_exist,
                                                  out_wallet.percentage,
                                                  out_wallet.amount - tx_amount)
                    balance = 0
                # set original out wallet to TransactionIntent
                out_wallet = [w for w in out_wallets if w.address == out_wallet.address][0]
                txs.append(TransactionIntent(
                    in_wallet=in_wallet,
                    out_wallet=out_wallet,
                    amount=tx_amount,
                    fee=fee
                ))
        return txs

    def _calculate_fee(self,
                       in_wallets: List[InputWallet],
                       intents: List[TransactionIntent]) -> int:
        total_fee = 0

        intents_by_wallet: Dict[InputWallet, List[TransactionIntent]] = {}
        for intent in intents:
            if intent.in_wallet not in intents_by_wallet:
                intents_by_wallet[intent.in_wallet] = []
            intents_by_wallet[intent.in_wallet].append(intent)

        created_wallet = set()
        for w in in_wallets:
            # print("_calculate_fee, input wallet:", w)
            available_bandwidth = w.available_bandwidth
            for intent in intents_by_wallet[w]:
                out_wallet = intent.out_wallet
                # if wallet doesn't created yet
                # also check that wallet will not be created twice
                if not out_wallet.is_exist \
                        and out_wallet.address not in created_wallet:
                    total_fee += self.create_account_fee
                    out_wallet.fee = self.create_account_fee
                    # print("_calculate_fee, fee for creating account", out_wallet.address)
                # free transactions
                elif available_bandwidth - self.transaction_points >= 0:
                    available_bandwidth -= self.transaction_points
                else:
                    out_wallet.fee = self.transaction_points * 10
                    total_fee += out_wallet.fee
                created_wallet.add(out_wallet.address)

        return total_fee

    def _check_calculations(self,
                            wallets: List[InputWallet],
                            intents: List[TransactionIntent],
                            total_fee):
        total = self._get_total_balance(wallets, total_fee=0)
        total_intents = sum([intent.amount for intent in intents])
        print("_check_calculations:", total_intents, "- total_intents")
        print("_check_calculations:", total, "- total,", total_fee, "- fee")
        assert total_intents == total - total_fee
