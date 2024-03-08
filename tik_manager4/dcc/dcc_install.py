"""Convenience functions for installing and integrating DCCs."""
import sys
import getopt
import logging


LOG = logging.getLogger(__name__)

class CLI:
    """A simple command line interface for installing software."""
    def __init__(self, argv):
        self.argv = argv

    def main(self):
        # parse the arguments
        opts, args = getopt.getopt(self.argv, "n:h:v", ["networkpath", "help", "verbose"])

        if not opts and not args:
            # cli()
            # LOG.info("testing: run cli() here")
            sys.stdout.write("testing: run cli() here")
        else:
            if not opts and args:
                # print("You must enter -n argument")
                # LOG.info("You must enter -n argument")
                sys.stdout.write("You must enter -n argument")
                sys.exit()

            network_path = ""
            for option, argument in opts:
                if option == "-n":
                    network_path = argument
                    sys.stdout.write("network_path: " + network_path)
                else:
                    assert False, "unhandled option"
                    # raw_input("Something went wrong.. Try manual installation")
                    r = input("Something went wrong.. Try manual installation")
                    assert isinstance(r, str)

            software_list = args


# def main(argv):
#     # parse the arguments
#     opts, args = getopt.getopt(argv, "n:h:v", ["networkpath", "help", "verbose"])
#
#     if not opts and not args:
#         # cli()
#         LOG.info("testing: run cli() here")
#         sys.stdout.write("Hello")
#     else:
#         if not opts and args:
#             # print("You must enter -n argument")
#             LOG.info("You must enter -n argument")
#             sys.exit()
#
#         network_path = ""
#         for option, argument in opts:
#             if option == "-n":
#                 network_path = argument
#             else:
#                 assert False, "unhandled option"
#                 # raw_input("Something went wrong.. Try manual installation")
#                 r = input("Something went wrong.. Try manual installation")
#                 assert isinstance(r, str)
#
#         software_list = args
#
#
#         # folderCheck(network_path)
#         LOG.info("testing: run folderCheck(network_path) here")
#         # print("network_path", network_path)
#         LOG.info("network_path", network_path)
#         # print("software_list", software_list)
#         LOG.info("software_list", software_list)
#
#         # noCli(network_path, software_list)
#         LOG.info("testing: run noCli(network_path, software_list) here")


if __name__ == "__main__":
    # main(sys.argv[1:])
    cli = CLI(sys.argv[1:])
    cli.main()