final: prev:

let
  py3 = final.python3;
  pyPkgs = py3.pkgs;
  buildPythonPackage = py3.pkgs.buildPythonPackage;
  fetchPypi = py3.pkgs.fetchPypi;
  defaultArguments = {
    inherit pyPkgs fetchPypi buildPythonPackage;
  };
in
{
  django-account = final.pkgs.callPackage ./django-account.nix defaultArguments;
  django-bootstrap-form = final.pkgs.callPackage ./django-bootstrap-form.nix defaultArguments;
  django-extensions = final.pkgs.callPackage ./django-extensions.nix defaultArguments;
  python-kanboard-api = final.pkgs.callPackage ./python-kanboard-api.nix defaultArguments;

  subtitleStatusCfg = final.pkgs.writeText "subtitleStatus.cfg" ''
    [sql]
    type=postgresql
    database=subtitlestatus
    user=subtitlestatus
    password=a_very_secure_password
  '';
}
