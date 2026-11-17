// Configuración de commitlint para KEFA AI
// Basado en Conventional Commits, extendido con el tipo "security"
// según decisión del equipo.

module.exports = {
  extends: ['@commitlint/config-conventional'],
  rules: {
    // Tipos de commit permitidos
    'type-enum': [
      2,
      'always',
      [
        'feat',     // nueva funcionalidad
        'fix',      // corrección de bug
        'docs',     // documentación
        'test',     // pruebas
        'refactor', // refactorización sin cambio de comportamiento
        'chore',    // tareas de mantenimiento / configuración
        'security', // cambios relacionados con seguridad
        'style',    // formato, sin cambios de lógica
        'perf',     // mejoras de rendimiento
        'build',    // build system / dependencias
        'ci',       // configuración de CI/CD
        'revert',   // revertir un commit anterior
      ],
    ],

    // El scope es obligatorio: debe llevar el ticket, ej. (KEFA-032)
    'scope-empty': [2, 'never'],

    // Se desactiva la restricción de minúsculas en el scope,
    // ya que los tickets usan el formato KEFA-XXX (mayúsculas)
    'scope-case': [0],
  },
};