{
  description = "subtitlesStatus, the c3subtitles.de frontend code";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-21.11";
    flake-utils.url = "github:numtide/flake-utils";
    flake-compat = {
      url = "github:edolstra/flake-compat";
      flake = false;
    };
    poetry2nix.url = "github:nix-community/poetry2nix";
  };

  outputs = { self, nixpkgs, flake-utils, poetry2nix, ... }@inputs:
    flake-utils.lib.eachDefaultSystem
      (system:
        let
          overlay = import ./nix;
          pkgs = import nixpkgs {
            inherit system;
            overlays = [
              overlay
              poetry2nix.overlay
            ];
          };
        in
        {
          inherit overlay;
          devShell =
            let
              poetryEnv = pkgs.poetry2nix.mkPoetryEnv {
                projectDir = ./.;
                overrides = pkgs.poetry2nix.overrides.withDefaults (self: super: { uwsgi = null; });
              };
            in
            poetryEnv.env.overrideAttrs
              (oldAttrs: {
                SUBTITLESTATUS_CONFIG = "${pkgs.subtitleStatusCfg}";
                buildInputs = [ pkgs.poetry ];
              });
        });
}
