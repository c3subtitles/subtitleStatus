final: prev:

let
  py3 = final.python3;
  pyPkgs = py3.pkgs;
  buildPythonPackage = py3.pkgs.buildPythonPackage;
  fetchPypi = py3.pkgs.fetchPypi;
in
{
  django-bootstrap-form = final.pkgs.callPackage ./django-bootstrap-form.nix { inherit pyPkgs fetchPypi buildPythonPackage; };
}
