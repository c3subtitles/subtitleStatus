{ lib, buildPythonPackage, fetchPypi, pyPkgs }:

buildPythonPackage rec {
  pname = "django-account";
  version = "0.1.14";
  meta = {
    description = "Accounts support for django";
    license = lib.licenses.bsd3;
    homepage = "https://pypi.org/project/django-account/";
  };

  src = fetchPypi {
    inherit pname version;
    sha256 = "sha256-S/5dHsfVn7OKolr+tzfVi9oGfGYnTvjxZSShNRMj8JE=";
  };

  buildInputs = with pyPkgs; [ django six ];
  propagatedBuildInputs = with pyPkgs; [ django six ];
  doCheck = false;
}
