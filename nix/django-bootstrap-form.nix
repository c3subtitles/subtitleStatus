{ lib, buildPythonPackage, fetchPypi, pyPkgs }:

buildPythonPackage rec {
  pname = "django-bootstrap-form";
  version = "3.4";
  meta = {
    description = "Twitter Bootstrap for Django Form";
    license = lib.licenses.mit;
    homepage = "https://github.com/tzangms/django-bootstrap-form";
  };

  src = fetchPypi {
    inherit pname version;
    sha256 = "sha256-3j94k+UVNSg01EbEQcDLhhY3+SzrvlnYIpRpxs09xkA=";
  };

  buildInputs = with pyPkgs; [ django six ];
  propagatedBuildInputs = with pyPkgs; [ django six ];
  doCheck = false;
}
