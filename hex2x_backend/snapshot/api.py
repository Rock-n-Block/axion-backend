from datetime import datetime

from hex2x_backend.tokenholders.models import TokenStakeStart, TokenStakeEnd, TokenTransfer
from hex2x_backend.tokenholders.common import HEX_WIN_TOKEN_ADDRESS
from .models import HexUser, SnapshotOpenedStake, SnapshotAddressHexBalance, SnapshotAddressSharesBalance
from holder_parsing import get_hex_balance_for_address, get_hex_balance_for_multiple_address
from .signing import get_user_signature
from .web3int import W3int
from holder_parsing import load_hex_contract

ETHEREUM_ZERO_ADDRESS = '0x0000000000000000000000000000000000000000'

def regenerate_db_amount_signatures():
    all_users = HexUser.objects.all().order_by('id')

    w3 = W3int('parity')
    hex_contract = load_hex_contract(w3.interface)

    for hex_user in all_users:
        try:
            print('Progress: {curr}/{total}'.format(curr=hex_user.id, total=len(all_users)), flush=True)
            #hex_user.hex_amount = get_hex_balance_for_multiple_address(w3.interface, hex_contract, hex_user.user_address)
            hex_user.hex_amount = get_hex_balance_for_address(hex_user.user_address)
            sign_info = get_user_signature('mainnet', hex_user.user_address, int(hex_user.hex_amount))
            hex_user.user_hash = sign_info['msg_hash'].hex()
            hex_user.hash_signature = sign_info['signature']
            hex_user.save()
        except Exception as e:
            print('error in parsing', hex_user.id, hex_user.user_address)
            print(e)


def regenerate_db_amount_signatures_from(count_start, count_stop=None):
    if not count_stop:
        count_stop=HexUser.objects.all().last().id

    all_users = HexUser.objects.filter(id__in=list(range(count_start, count_stop)))

    w3 = W3int('parity')
    hex_contract = load_hex_contract(w3.interface)

    for hex_user in all_users:
        print('Progress: {curr}/{total}'.format(curr=hex_user.id, total=len(all_users)), flush=True)
        hex_user.hex_amount = get_hex_balance_for_multiple_address(w3.interface, hex_contract, hex_user.user_address)
        sign_info = get_user_signature('mainnet', hex_user.user_address, int(hex_user.hex_amount))
        hex_user.user_hash = sign_info['msg_hash'].hex()
        hex_user.hash_signature = sign_info['signature']
        hex_user.save()


def generate_and_save_signature(hex_user, network='mainnet'):
    sign_info = get_user_signature(network, hex_user.user_address, int(hex_user.hex_amount))
    hex_user.user_hash = sign_info['msg_hash'].hex()
    hex_user.hash_signature = sign_info['signature']
    hex_user.save()
    print('user:', hex_user.user_address, 'hash:', hex_user.user_hash, 'signature:', hex_user.hash_signature)


def make_opened_stake_snapshot():
    started_stakes = TokenStakeStart.objects.all()

    for stake in started_stakes:
        ended_stake = TokenStakeEnd.objects.filter(address=stake.address, stake_id=stake.id)
        if len(ended_stake) == 1:
            opened_stake = SnapshotOpenedStake(
                address=stake.address,
                stake_id=stake.stake_id,
                data0=stake.data0,
                timestamp=stake.timestamp,
                hearts=stake.hearts,
                shares=stake.shares,
                days=stake.days,
                is_autostake=stake.is_autostake,
                tx_hash=stake.tx_hash,
                block_number=stake.block_number
            )

            opened_stake.save()

            print('Saved started stake',
                  opened_stake.id, opened_stake.address, opened_stake.stake_id, opened_stake.data0,
                  opened_stake.timestamp, opened_stake.hearts, opened_stake.shares, opened_stake.days,
                  opened_stake.is_autostake, opened_stake.tx_hash
                  )
        elif len(ended_stake) == 0:
            continue
        else:
            print('multiple results found for', stake.id, 'skipping')


def make_balance_snapshot():
    all_transfers = TokenTransfer.objects.all().order_by('id')

    print('Balance snapshot started', flush=True)
    print(str(datetime.now()), flush=True)
    for transfer in all_transfers:
        if transfer.parsed:
            print(str(datetime.now()), 'skipping transfer', transfer.id, 'because already parsed', flush=True)
            continue
        if transfer.from_address == transfer.to_address:
            print(str(datetime.now()), 'skipping transfer', transfer.id, 'because from and to addresses matched',
                  flush=True)
            continue

        if transfer.from_address != ETHEREUM_ZERO_ADDRESS:
            snapshot_address_1, created = SnapshotAddressHexBalance.objects.get_or_create(address=transfer.from_address)
            snapshot_address_1.balance -= transfer.amount
            snapshot_address_1.save()
            print(str(datetime.now()), 'Block', transfer.block_number, 'transfer', transfer.id,
                  'address_1', snapshot_address_1.address, 'updated, balance:', snapshot_address_1.balance,
                  flush=True
                  )

        if transfer.to_address not in [ETHEREUM_ZERO_ADDRESS, HEX_WIN_TOKEN_ADDRESS]:
            snapshot_address_2, created = SnapshotAddressHexBalance.objects.get_or_create(address=transfer.to_address)
            snapshot_address_2.balance += transfer.amount
            snapshot_address_2.save()
            print(str(datetime.now()), 'Block', transfer.block_number, 'transfer', transfer.id,
                  'address_2', snapshot_address_2.address, 'updated, balance:', snapshot_address_2.balance,
                  flush=True
                  )

        transfer.parsed = True
        transfer.save()

    print('Balance snapshot done', flush=True)
    print(str(datetime.now()), flush=True)
    return


def make_balance_shares_snapshot():
    unique_addresses = [addr['address'] for addr in SnapshotOpenedStake.objects.values('address').distinct()]

    print('Shares snapshot started', str(datetime.now()), flush=True)
    for address in unique_addresses:
        snapshot_address, created = SnapshotAddressSharesBalance.objects.get_or_create(address=address)
        if created:
            snapshot_address.save()

        stakes_for_address = SnapshotOpenedStake.objects.filter(address=address)

        for stake in stakes_for_address:
            if not stake.parsed:
                snapshot_address.balance += stake.shares
                stake.parsed = True

        snapshot_address.save()
        print(str(datetime.now()),
              'address', address, 'stakes len', len(stakes_for_address), 'shares amount', snapshot_address.balance,
              flush=True)

    print('Shares snapshot ended', str(datetime.now()), flush=True)


def make_full_hex_user_snapshot():
    print('Full hex user snapshot started', str(datetime.now()), flush=True)

    for user in SnapshotAddressHexBalance.objects.all():
        hex_balance = user.balance
        shares_snapshot = SnapshotAddressSharesBalance.objects.filter(address=user.address)
        share_amount = shares_snapshot.first().balance if shares_snapshot else 0
        total_balance = hex_balance + share_amount

        sign_info = get_user_signature('mainnet', user.address, int(total_balance))
        hash = sign_info['msg_hash'].hex()
        signature = sign_info['signature']

        hex_user = HexUser(
            user_address=user.address,
            hex_amount=total_balance,
            user_hash=hash,
            hash_signature=signature
        )

        hex_user.save()

        print(str(datetime.now()),
              'id', hex_user.id, 'address', hex_user.user_address, 'amount', hex_user.hex_amount,
              'hash', hex_user.user_hash, 'signature', hex_user.hash_signature, flush=True
              )

    print('Full hex user snapshot completed', str(datetime.now()), flush=True)

