{ lib, buildPythonPackage, fetchPypi, pyPkgs }:

buildPythonPackage rec {
  pname = "django-extensions";
  version = "2.2.5";
  #version = "3.1.5";
  meta = {
    description = "A collection of custom extensions for the Django Framework";
    license = lib.licenses.mit;
    homepage = "https://github.com/django-extensions/django-extensions";
  };

  src = fetchPypi {
    inherit pname version;
    sha256 = "sha256-tYMg0/49aufR2OOJWXE/qSJy9JIeZi1okFjZQqW0RPc=";
  };

  buildInputs = with pyPkgs; [ django six ];
  propagatedBuildInputs = with pyPkgs; [ django six ];
  doCheck = false;
}
