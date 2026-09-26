#version 330 core

in vec3 normal_view;
in vec3 viewDir_view;
in vec2 uv;
in vec3 lightDir_view;

out vec4 fragColor;

uniform sampler2D planetTex;          // planet texture
uniform sampler2D emissionTex;
uniform vec3 atmosphereColor = vec3(0.5, 0.7, 1.0);
uniform float intensity = 1.5;
uniform float level = 1.5;

void main() {
    vec3 baseColor = texture(planetTex, uv).rgb;
    vec3 emission = texture(emissionTex, uv).rgb;

    // Diffuse
    float lighting = max(dot(normal_view, lightDir_view), 0.0);

    vec3 litPlanet = baseColor * lighting;

    // atm edge glow
    float edgeFactor = level*1.5 - max(dot(normal_view, viewDir_view), 0.0);
    float glow = pow(edgeFactor, 2.0) * intensity*0.2;
    float nightFactor = (1.0 - lighting)*0.8;

    vec3 color = litPlanet + glow * atmosphereColor * lighting + emission * nightFactor;

    fragColor = vec4(color, 1.0);
}
