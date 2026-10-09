vec4 effect(vec2 uv) {
 vec2 p=(uv-vec2(0.5))*vec2(1.0,1.15);
 float accum=0.0;
 for(int i=0;i<24;i++) {
  float z=float(i)/24.0;
  vec2 q=p*(0.8+z*0.5);
  float f=sin(q.x*9.0+z*5.0+iTime)*cos(q.y*7.0-z*6.0+iTime*0.7);
  accum+=exp(-7.0*length(q))*max(0.0,f)*0.055;
 }
 vec3 c=vec3(0.025,0.055,0.075)+accum*vec3(0.4,1.1,0.9);
 return vec4(c,1.0);
}
void mainImage(out vec4 fragColor, in vec2 fragCoord) {
 fragColor=effect(fragCoord/iResolution.xy);
}