{
  description = "subtitlesStatus, the c3subtitles.de frontend code";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-22.05";
    utils.url = "github:gytis-ivaskevicius/flake-utils-plus";
    poetry2nix = {
      url = "github:nix-community/poetry2nix";
      inputs = {
        nixpkgs.follows = "nixpkgs";
        flake-utils.follows = "utils/flake-utils";
      };
    };
  };

  outputs = { self, nixpkgs, utils, poetry2nix, ... }@inputs:
    let overlay = import ./nix;
    in utils.lib.mkFlake {
      inherit self inputs overlay;

      sharedOverlays = [ poetry2nix.overlay overlay ];

      outputsBuilder = channels: {
        devShell = let
          poetryEnv = channels.nixpkgs.poetry2nix.mkPoetryEnv {
            projectDir = ./.;
            overrides = channels.nixpkgs.poetry2nix.overrides.withDefaults
              (self: super: {
                uwsgi = null;
                cryptography = super.cryptography.overridePythonAttrs (old: {
                  cargoDeps = channels.nixpkgs.rustPlatform.fetchCargoTarball {
                    inherit (old) src;
                    name = "${old.pname}-${old.version}";
                    sourceRoot = "${old.pname}-${old.version}/src/rust/";
                    sha256 =
                      "sha256-f8r6QclTwkgK20CNe9i65ZOqvSUeDc4Emv6BFBhh1hI=";
                  };
                  cargoRoot = "src/rust";
                  nativeBuildInputs = old.nativeBuildInputs
                    ++ (with channels.nixpkgs.rustPlatform; [
                      rust.rustc
                      rust.cargo
                      cargoSetupHook
                    ]);
                });

              });
          };
        in poetryEnv.env.overrideAttrs (oldAttrs: {
          SUBTITLESTATUS_CONFIG = "${channels.nixpkgs.subtitleStatusCfg}";
          buildInputs = [ channels.nixpkgs.poetry ];
        });
      };
    };
}
