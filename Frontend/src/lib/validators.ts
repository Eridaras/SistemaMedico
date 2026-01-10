/**
 * Valida una cédula ecuatoriana según el algoritmo del dígito verificador
 * @param cedula - Cédula de 10 dígitos
 * @returns true si la cédula es válida
 */
export function validateEcuadorianCedula(cedula: string): boolean {
  // Debe tener exactamente 10 dígitos
  if (!/^\d{10}$/.test(cedula)) {
    return false;
  }

  // Los dos primeros dígitos deben corresponder a una provincia válida (01-24)
  const provincia = parseInt(cedula.substring(0, 2));
  if (provincia < 1 || provincia > 24) {
    return false;
  }

  // El tercer dígito debe ser menor a 6 (0-5)
  const tercerDigito = parseInt(cedula.charAt(2));
  if (tercerDigito > 5) {
    return false;
  }

  // Validar dígito verificador usando el algoritmo módulo 10
  const coeficientes = [2, 1, 2, 1, 2, 1, 2, 1, 2];
  const digitoVerificador = parseInt(cedula.charAt(9));

  let suma = 0;
  for (let i = 0; i < 9; i++) {
    let valor = parseInt(cedula.charAt(i)) * coeficientes[i];
    if (valor >= 10) {
      valor -= 9;
    }
    suma += valor;
  }

  const resultado = suma % 10;
  const digitoEsperado = resultado === 0 ? 0 : 10 - resultado;

  return digitoVerificador === digitoEsperado;
}
