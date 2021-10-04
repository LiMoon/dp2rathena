import os
import re

import pytest

from pathlib import Path
from click.testing import CliRunner
from dp2rathena import cli


def test_config_filesystem():
    runner = CliRunner()
    result = runner.invoke(cli.dp2rathena, ['config'], input="123")
    assert 'Enter your Divine-Pride API key:' in result.output
    assert 'Configuration saved to' in result.output


def test_dp2rathena():
    runner = CliRunner()
    result = runner.invoke(cli.dp2rathena)
    assert not result.exception
    result = runner.invoke(cli.dp2rathena, ['--api-key'])
    assert result.exception
    assert 'Error: --api-key option requires an argument' in result.output
    result = runner.invoke(cli.dp2rathena, ['--api-key', 'hello'])
    assert result.exception
    assert 'is not a 32-character hexadecimal string' in result.output
    result = runner.invoke(cli.dp2rathena, ['--api-key', '12345678aaaabbbb00000000ffffffff'])
    assert result.exception
    assert 'Missing command' in result.output
    with runner.isolated_filesystem():
        env_path = Path('.') / '.env'
        env_path.write_text('DIVINEPRIDE_API_KEY=abc123\n')
        result = runner.invoke(cli.dp2rathena)
        assert not result.exception
    with runner.isolated_filesystem():
        config_path = Path.home() / '.dp2rathena.conf'
        config_path.write_text('DIVINEPRIDE_API_KEY=abc123\n')
        result = runner.invoke(cli.dp2rathena)
        assert not result.exception


def test_version():
    runner = CliRunner()
    result = runner.invoke(cli.dp2rathena, ['version'])
    assert not result.exception
    assert re.fullmatch(r'\d+\.\d+\.\d+', result.output.rstrip())


def test_config():
    runner = CliRunner()
    config_path = Path.home() / '.dp2rathena.conf'
    with runner.isolated_filesystem():
        result = runner.invoke(cli.dp2rathena, ['config'], input="abc-123")
        assert not result.exception
        assert 'Enter your Divine-Pride API key:' in result.output
        assert 'Configuration saved to' in result.output
        assert config_path.exists()
        result = runner.invoke(cli.dp2rathena, ['config'], input="aaaabbbbccccdddd1111222233334444")
        assert not result.exception
        assert 'Enter your Divine-Pride API key:' in result.output
        assert 'Configuration saved to' in result.output
        assert config_path.exists()


def test_item_invalid(fixture):
    runner = CliRunner()
    result = runner.invoke(cli.dp2rathena, ['item'])
    assert result.exit_code == 2
    assert 'Item id required' in result.output
    result = runner.invoke(cli.dp2rathena, ['item', 'hello'])
    assert result.exit_code == 2
    assert 'Non-integer item id' in result.output
    result = runner.invoke(cli.dp2rathena, ['item', 'hello', 'world'])
    assert result.exit_code == 2
    assert 'Non-integer item id' in result.output
    result = runner.invoke(cli.dp2rathena, ['item', '-f'])
    assert result.exit_code == 2
    assert 'One file required for processing' in result.output
    result = runner.invoke(cli.dp2rathena, ['item', '-f', 'missing.txt'])
    assert result.exit_code == 1
    assert isinstance(result.exception, FileNotFoundError)
    result = runner.invoke(cli.dp2rathena, ['item', '123', '-f', fixture('1101_501.txt')])
    assert result.exit_code == 2
    assert 'One file required for processing' in result.output


def test_item_invalid_config():
    runner = CliRunner()
    with runner.isolated_filesystem():
        env_path = Path('.') / '.env'
        env_path.write_text('')
        result = runner.invoke(cli.dp2rathena, ['item', '501'])
        assert result.exit_code == 1
        assert isinstance(result.exception, KeyError)
    with runner.isolated_filesystem():
        config_path = Path.home() / '.dp2rathena.conf'
        config_path.write_text('')
        result = runner.invoke(cli.dp2rathena, ['item', '501'])
        assert result.exit_code == 1
        assert isinstance(result.exception, KeyError)


# These tests could fail if DP API is down
# def test_item_flaky():
#     runner = CliRunner()
#     result = runner.invoke(cli.dp2rathena, ['-k', 'aaaabbbbccccdddd1111222233334444', 'item', '501'])
#     assert result.exit_code == 1
#     assert isinstance(result.exception, IOError)


@pytest.mark.api
def test_item_valid(fixture):
    runner = CliRunner()
    with open(fixture('item_501.yml'), encoding='utf-8') as f:
        expected = f.read()
        result = runner.invoke(cli.dp2rathena, ['item', '501'])
        assert result.exit_code == 0
        assert result.output == expected
        result = runner.invoke(cli.dp2rathena, ['item', '-f', '-'], input='501')
        assert result.exit_code == 0
        assert result.output == expected
    with open(fixture('item_501_1101.yml'), encoding='utf-8') as f:
        expected = f.read()
        result = runner.invoke(cli.dp2rathena, ['item', '501', '1101'])
        assert result.exit_code == 0
        assert result.output == expected
        result = runner.invoke(cli.dp2rathena, ['item', '--sort', '1101', '501'])
        assert result.exit_code == 0
        assert result.output == expected
        result = runner.invoke(cli.dp2rathena, ['item', '-f', fixture('1101_501.txt'), '--sort'])
        assert result.exit_code == 0
        assert result.output == expected
        result = runner.invoke(cli.dp2rathena, ['item', '-f', '-', '--sort'], input='1101\n501')
        assert result.exit_code == 0
        assert result.output == expected
    with open(fixture('item_1101_501.yml'), encoding='utf-8') as f:
        expected = f.read()
        result = runner.invoke(cli.dp2rathena, ['item', '-f', fixture('1101_501.txt')])
        assert result.exit_code == 0
        assert result.output == expected
    with open(fixture('item_900_1101.yml'), encoding='utf-8') as f:
        expected = f.read()
        result = runner.invoke(cli.dp2rathena, ['item', '900', '1101', '--sort'])
        assert result.exit_code == 0
        assert result.output == expected


def test_mob_skill_invalid(fixture):
    runner = CliRunner()
    result = runner.invoke(cli.dp2rathena, ['mobskill'])
    assert result.exit_code == 2
    assert 'Mob id required' in result.output
    result = runner.invoke(cli.dp2rathena, ['mobskill', 'hello'])
    assert result.exit_code == 2
    assert 'Non-integer mob id' in result.output
    result = runner.invoke(cli.dp2rathena, ['mobskill', 'hello', 'world'])
    assert result.exit_code == 2
    assert 'Non-integer mob id' in result.output
    result = runner.invoke(cli.dp2rathena, ['mobskill', '-f'])
    assert result.exit_code == 2
    assert 'One file required for processing' in result.output
    result = runner.invoke(cli.dp2rathena, ['mobskill', '-f', 'missing.txt'])
    assert result.exit_code == 1
    assert isinstance(result.exception, FileNotFoundError)
    result = runner.invoke(cli.dp2rathena, ['mobskill', '123', '-f', fixture('1101_501.txt')])
    assert result.exit_code == 2
    assert 'One file required for processing' in result.output


# These tests could fail if DP API is down
# def test_mob_skill_flaky():
#     runner = CliRunner()
#     result = runner.invoke(cli.dp2rathena, ['-k', 'aaaabbbbccccdddd1111222233334444', 'mobskill', '1002'])
#     assert result.exit_code == 1
#     assert isinstance(result.exception, IOError)


@pytest.mark.api
def test_mob_skill_valid(fixture):
    runner = CliRunner()
    with open(fixture('mob_skill_1002.txt'), encoding='utf-8') as f:
        expected = f.read()
        result = runner.invoke(cli.dp2rathena, ['mobskill', '1002'])
        assert result.exit_code == 0
        assert result.output == expected
        result = runner.invoke(cli.dp2rathena, ['mobskill', '-f', '-'], input='1002')
        assert result.exit_code == 0
        assert result.output == expected
    with open(fixture('mob_skill_3212.txt'), encoding='utf-8') as f:
        expected = f.read()
        result = runner.invoke(cli.dp2rathena, ['mobskill', '--comment', '3212'])
        assert result.exit_code == 0
        assert result.output == expected
    with open(fixture('mob_skill_1002_1049.txt'), encoding='utf-8') as f:
        expected = f.read()
        result = runner.invoke(cli.dp2rathena, ['mobskill', '1002', '1049'])
        assert result.exit_code == 0
        assert result.output == expected
        result = runner.invoke(cli.dp2rathena, ['mobskill', '-f', fixture('1002_1049.txt')])
        assert result.exit_code == 0
        assert result.output == expected
    with open(fixture('mob_skill_1049_1002.txt'), encoding='utf-8') as f:
        expected = f.read()
        result = runner.invoke(cli.dp2rathena, ['mobskill', '-f', '-'], input='1049\n1002')
        assert result.exit_code == 0
        assert result.output == expected


def test_mob_invalid(fixture):
    runner = CliRunner()
    result = runner.invoke(cli.dp2rathena, ['mob'])
    assert result.exit_code == 2
    assert 'Mob id required' in result.output
    result = runner.invoke(cli.dp2rathena, ['mob', 'hello'])
    assert result.exit_code == 2
    assert 'Non-integer mob id' in result.output
    result = runner.invoke(cli.dp2rathena, ['mob', 'hello', 'world'])
    assert result.exit_code == 2
    assert 'Non-integer mob id' in result.output
    result = runner.invoke(cli.dp2rathena, ['mob', '-f'])
    assert result.exit_code == 2
    assert 'One file required for processing' in result.output
    result = runner.invoke(cli.dp2rathena, ['mob', '-f', 'missing.txt'])
    assert result.exit_code == 1
    assert isinstance(result.exception, FileNotFoundError)
    result = runner.invoke(cli.dp2rathena, ['mob', '123', '-f', fixture('20355_1002.txt')])
    assert result.exit_code == 2
    assert 'One file required for processing' in result.output


def test_mob_invalid_config():
    runner = CliRunner()
    with runner.isolated_filesystem():
        env_path = Path('.') / '.env'
        env_path.write_text('')
        result = runner.invoke(cli.dp2rathena, ['mob', '1002'])
        assert result.exit_code == 1
        assert isinstance(result.exception, KeyError)
    with runner.isolated_filesystem():
        config_path = Path.home() / '.dp2rathena.conf'
        config_path.write_text('')
        result = runner.invoke(cli.dp2rathena, ['mob', '1002'])
        assert result.exit_code == 1
        assert isinstance(result.exception, KeyError)


# These tests could fail if DP API is down
# def test_mob_flaky():
#     runner = CliRunner()
#     result = runner.invoke(cli.dp2rathena, ['-k', 'aaaabbbbccccdddd1111222233334444', 'mob', '1002'])
#     assert result.exit_code == 1
#     assert isinstance(result.exception, IOError)


@pytest.mark.api
def test_mob_valid(fixture):
    runner = CliRunner()
    with open(fixture('mob_1002.yml'), encoding='utf-8') as f:
        expected = f.read()
        result = runner.invoke(cli.dp2rathena, ['mob', '1002'])
        assert result.exit_code == 0
        assert result.output == expected
        result = runner.invoke(cli.dp2rathena, ['mob', '-f', '-'], input='1002')
        assert result.exit_code == 0
        assert result.output == expected
    with open(fixture('mob_1002_1049.yml'), encoding='utf-8') as f:
        expected = f.read()
        result = runner.invoke(cli.dp2rathena, ['mob', '1002', '1049'])
        assert result.exit_code == 0
        assert result.output == expected
        result = runner.invoke(cli.dp2rathena, ['mob', '--sort', '1049', '1002'])
        assert result.exit_code == 0
        assert result.output == expected
        result = runner.invoke(cli.dp2rathena, ['mob', '-f', fixture('1049_1002.txt'), '--sort'])
        assert result.exit_code == 0
        assert result.output == expected
        result = runner.invoke(cli.dp2rathena, ['mob', '-f', '-', '--sort'], input='1049\n1002')
        assert result.exit_code == 0
        assert result.output == expected
    with open(fixture('mob_1049_1002.yml'), encoding='utf-8') as f:
        expected = f.read()
        result = runner.invoke(cli.dp2rathena, ['mob', '-f', fixture('1049_1002.txt')])
        assert result.exit_code == 0
        assert result.output == expected