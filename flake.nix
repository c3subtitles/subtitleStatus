{
  description = "subtitlesStatus, the c3subtitles.de frontend code";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-21.11";
    flake-utils.url = "github:numtide/flake-utils";
    flake-compat = {
      url = "github:edolstra/flake-compat";
      flake = false;
    };
  };

  outputs = { self, nixpkgs, flake-utils, ... }@inputs:
    flake-utils.lib.eachDefaultSystem (system:
      let
        overlay = import ./nix;
        pkgs = import nixpkgs {
          inherit system;
          overlays = [ overlay ];
        };
      in
      {
        inherit overlay;
        devShell = pkgs.mkShell {
          buildInputs = [
            (pkgs.python3.withPackages (pyPkgs: with pyPkgs; [
              django
              pkgs.django-account
              pkgs.django-bootstrap-form
              pkgs.django-extensions
              django-pglocks
              factory_boy
              faker
              google-api-python-client
              google-auth
              google-auth-httplib2
              httplib2
              isodate
              pkgs.python-kanboard-api
              lxml
              oauth2client
              paramiko
              psycopg2
              pyasn1
              pyasn1-modules
              pynacl
              pysftp
              python-dateutil
              pytz
              requests
              rsa
              simplejson
              six
              sqlparse
              text-unidecode
              twitter
              uritemplate
              urllib3
              (pkgs.uwsgi.override
                { plugins = [ "python3" ]; })
              xmltodict
              pip
            ]))

          ];
        };
      });

}
