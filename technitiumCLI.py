from technitiumAPI import TechnitiumAPI
from argparse import ArgumentParser
import sys

class CLIException(Exception):
    pass

def main(cliArgs: list=sys.argv[1:]):
    # Main parser
    parser = ArgumentParser(prog="Technitium DNS Server CLI")
    parser.add_argument("--host", help="The Technitium DNS Server host.", nargs='?')
    parser.add_argument("--username", help="The Technitium DNS Server username.", nargs='?')
    parser.add_argument("--password", help="The Technitium DNS Server password.", nargs='?')
    parser.add_argument("--port", help="The port to connect to.", nargs='?', type=int, default=5380)

    items = parser.add_subparsers(help="The supported items to operate on.", dest="item")

    # Record parser
    record_parser = items.add_parser("record")
    operations = record_parser.add_subparsers(help="The operation to perform", dest="operation")
    # Add Record parser
    record_add_parser = operations.add_parser("add")
    record_add_parser.add_argument("zone", help="The zone to add to.")
    record_add_parser.add_argument("subdomain", help="The subdomain to add.")
    record_add_parser.add_argument("ip", help="The ip the record points to.")

    args = parser.parse_args(cliArgs)

    if args.item == 'record':
        if args.operation == 'add':
            __validate_options(args)
            __add_record(args)
        else:
            parser.print_help()
            sys.exit(1)
    else:
        parser.print_help()
        sys.exit(1)
    
    print("Success")

def __validate_options(args):
    def throwRequiredOptionException(option: str):
        parsed_option = option
        while parsed_option.startswith('-'):
            parsed_option = parsed_option[1:]

        value = getattr(args, parsed_option)
        if value is None:
            raise CLIException(f'The option \'{option}\' is undefined.')

    throwRequiredOptionException("--host")
    throwRequiredOptionException("--username")
    throwRequiredOptionException("--password")
    throwRequiredOptionException("--port")

def __add_record(args):
    with TechnitiumAPI(args.host, args.port, args.username, args.password) as server:
        zones = server.get_zones()
        zoneFound = False
        for zone in zones:
            if zone['name'] == args.zone:
                zoneFound = True
                break
        
        if zoneFound is False:
            raise CLIException(f'The zone \'{args.zone}\' could not be found.')
        
        records = server.get_records(args.zone)
        recordExists = False
        for record in records:
            if record['name'] == f'{args.subdomain}.{args.zone}':
                recordExists = True
                break
        
        if recordExists is True:
            raise CLIException(f'The record for \'{args.subdomain}.{args.zone}\' already exists.')
        
        server.add_record(args.zone, args.subdomain, args.ip)

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f'Exception occurred: {str(e)}')
        sys.exit(1)
    