#version 330 core

in vec4 p3d_Vertex;
in vec3 p3d_Normal;
in vec2 p3d_MultiTexCoord0;

out vec3 normal_view;     // normal in view space
out vec3 viewDir_view;    // view direction in view space
out vec2 uv;
out vec3 lightDir_view;   // light direction transformed to view space

uniform mat4 p3d_ModelViewMatrix;
uniform mat4 p3d_ProjectionMatrix;
uniform mat3 p3d_NormalMatrix; // transforms normals to view space
uniform vec3 lightDirWorld;    // directional light in WORLD space (normalize this in app)

void main() {
    // Position in view space
    vec4 pos_view = p3d_ModelViewMatrix * p3d_Vertex;
    // Normal already transformed to view space by p3d_NormalMatrix
    normal_view = normalize(p3d_NormalMatrix * p3d_Normal);

    // view direction (from surface to camera) in view space:
    viewDir_view = normalize(-pos_view.xyz);

    // Transform world-space light direction into view space.
    // Use the 3x3 part of the modelview (no translation) to transform direction vectors.
    lightDir_view = normalize(mat3(p3d_ModelViewMatrix) * lightDirWorld);

    uv = p3d_MultiTexCoord0;

    gl_Position = p3d_ProjectionMatrix * pos_view;
}
