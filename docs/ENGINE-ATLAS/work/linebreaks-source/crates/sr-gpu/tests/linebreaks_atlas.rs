//! Manual native-render evidence harness, outside the engine worktree diff.
mod common;
use common::*;
#[test]
fn render_source_atlas_and_legacy_reference() {
    let dir=std::path::PathBuf::from(std::env::var("SR_LINEBREAKS_ATLAS_DIR").expect("evidence directory"));
    let gpu=gpu().expect("software Vulkan adapter");
    let save=|pixels:Vec<[f32;4]>,size:[u32;2],path:std::path::PathBuf| {
        let transfer=|v:f32|if v<=0.0031308 {12.92*v} else {1.055*v.max(0.0).powf(1.0/2.4)-0.055};
        let bytes:Vec<u8>=pixels.into_iter().flat_map(|p| [
            (255.0*transfer(p[0]).clamp(0.0,1.0)).round() as u8,
            (255.0*transfer(p[1]).clamp(0.0,1.0)).round() as u8,
            (255.0*transfer(p[2]).clamp(0.0,1.0)).round() as u8,
            (255.0*p[3].clamp(0.0,1.0)).round() as u8,
        ]).collect();image::RgbaImage::from_raw(size[0],size[1],bytes).unwrap().save(path).unwrap();
    };
    for (source,frames) in [("scene.xml",84),("legacy.scene.xml",1)] {
        let doc=sr_model::load_file(dir.join(source),&sr_model::LoadOptions::default()).unwrap();
        let ev=sr_eval::Evaluator::new(&doc,&Default::default()).unwrap();let mut renderer=sr_gpu::Renderer::new(gpu.clone(),ev.program());
        std::fs::create_dir_all(dir.join("frames")).unwrap();
        for i in 0..frames {
            let time=if frames==1 {1.75} else {i as f64/24.0};let graph=ev.evaluate(time);let frame=renderer.render(&graph,ev.program());
            assert!(frame.stats.errors.is_empty(),"{:?}",frame.stats.errors);assert!(frame.stats.unsupported.is_empty(),"{:?}",frame.stats.unsupported);
            let out=if frames==1 {dir.join("legacy-source-test.png")} else {dir.join(format!("frames/{i:04}.png"))};
            save(renderer.read(&frame.texture),frame.texture.size,out);
        }
    }
}
