import { useEffect, useRef } from 'react';
import { useOrder } from '../context/OrderContext';
import { baguetteWidthPixels, previewGeometry } from '../utils/previewGeometry';

const DEFAULT_FRAME_WIDTH = 50;
const PASSEPARTOUT_COLOR = '#f5f5dc';
// Соответствует frame-tool3.html: ориентация полосок багета для митров
const ORIENT = {
  topFlipY: false,
  bottomFlipY: true,
  rightFlipX: false,
  leftRotate: 270,
};

export const FramePreview = ({ showLabel = true }) => {
  const { orderData, paintingImage } = useOrder();
  const canvasRef = useRef(null);
  const containerRef = useRef(null);
  const renderVersion = useRef(0);

  const getAllLayers = () => {
    const frames = orderData.frames || [];
    const layers = [];
    for (const frame of frames) {
      if (frame?.baguette_id || orderData.baguette_id) {
        const img = frame?.baguette_image || orderData.baguette_image;
        const w = frame?.baguette_width ?? orderData.baguette_width;
        layers.push({ type: 'baguette', image: img, width: w });
      }
    }
    return layers;
  };

  const makeStripCanvas = (imgOrCanvas, { rotate = 0, flipX = false, flipY = false } = {}) => {
    const srcW = imgOrCanvas.width ?? imgOrCanvas.naturalWidth;
    const srcH = imgOrCanvas.height ?? imgOrCanvas.naturalHeight;
    const off = document.createElement('canvas');
    const octx = off.getContext('2d');
    const rot = ((rotate % 360) + 360) % 360;
    const rot90like = rot === 90 || rot === 270;
    off.width = rot90like ? srcH : srcW;
    off.height = rot90like ? srcW : srcH;
    octx.save();
    octx.translate(off.width / 2, off.height / 2);
    if (rot === 90) octx.rotate(Math.PI / 2);
    if (rot === 270) octx.rotate(-Math.PI / 2);
    octx.scale(flipX ? -1 : 1, flipY ? -1 : 1);
    octx.drawImage(imgOrCanvas, -srcW / 2, -srcH / 2);
    octx.restore();
    return off;
  };

  const round = (v) => Math.round(v);
  const roundPoly = (pts) => pts.map(([a, b]) => [round(a), round(b)]);

  const clipPolygon = (ctx, points) => {
    const pts = roundPoly(points);
    ctx.beginPath();
    ctx.moveTo(pts[0][0], pts[0][1]);
    for (let i = 1; i < pts.length; i++) ctx.lineTo(pts[i][0], pts[i][1]);
    ctx.closePath();
    ctx.clip();
  };

  // Как в frame-tool3: полоска тайлится по длине, масштабируется по толщине (fw)
  const drawLengthwiseTiledStrip = (ctx, canvas, { stripCanvas, polygonPoints, orientation, fixedX, fixedY, fw }) => {
    ctx.save();
    clipPolygon(ctx, polygonPoints);
    const sw = stripCanvas.width;
    const sh = stripCanvas.height;
    const fixX = round(fixedX);
    const fixY = round(fixedY);
    if (orientation === 'h') {
      const startX = -sw;
      const endX = canvas.width + sw;
      for (let x = startX; x < endX; x += sw) ctx.drawImage(stripCanvas, 0, 0, sw, sh, x, fixY, sw, fw);
    } else {
      const startY = -sh;
      const endY = canvas.height + sh;
      for (let y = startY; y < endY; y += sh) ctx.drawImage(stripCanvas, 0, 0, sw, sh, fixX, y, fw, sh);
    }
    ctx.restore();
  };

  const drawFrameLayer = (ctx, canvas, { contentRect, texImgOrCanvas, fw }) => {
    const { x, y, w, h } = contentRect;
    const fwInt = Math.round(fw);
    const ox = round(x - fwInt);
    const oy = round(y - fwInt);
    const ow = round(w + 2 * fwInt);
    const oh = round(h + 2 * fwInt);
    let stripTop, stripBottom, stripLeft, stripRight;
    stripTop = makeStripCanvas(texImgOrCanvas, { rotate: 0, flipY: ORIENT.topFlipY });
    stripBottom = makeStripCanvas(texImgOrCanvas, { rotate: 0, flipY: ORIENT.bottomFlipY });
    stripLeft = makeStripCanvas(texImgOrCanvas, { rotate: ORIENT.leftRotate });
    stripRight = makeStripCanvas(texImgOrCanvas, { rotate: 90, flipX: ORIENT.rightFlipX });
    const topPoly = [[ox, oy], [ox + ow, oy], [ox + ow - fwInt, oy + fwInt], [ox + fwInt, oy + fwInt]];
    const bottomPoly = [[ox + fwInt, oy + oh - fwInt], [ox + ow - fwInt, oy + oh - fwInt], [ox + ow, oy + oh], [ox, oy + oh]];
    const leftPoly = [[ox, oy], [ox + fwInt, oy + fwInt], [ox + fwInt, oy + oh - fwInt], [ox, oy + oh]];
    const rightPoly = [[ox + ow - fwInt, oy + fwInt], [ox + ow, oy], [ox + ow, oy + oh], [ox + ow - fwInt, oy + oh - fwInt]];
    drawLengthwiseTiledStrip(ctx, canvas, { stripCanvas: stripTop, polygonPoints: topPoly, orientation: 'h', fixedX: 0, fixedY: oy, fw: fwInt });
    drawLengthwiseTiledStrip(ctx, canvas, { stripCanvas: stripBottom, polygonPoints: bottomPoly, orientation: 'h', fixedX: 0, fixedY: oy + oh - fwInt, fw: fwInt });
    drawLengthwiseTiledStrip(ctx, canvas, { stripCanvas: stripLeft, polygonPoints: leftPoly, orientation: 'v', fixedX: ox, fixedY: 0, fw: fwInt });
    drawLengthwiseTiledStrip(ctx, canvas, { stripCanvas: stripRight, polygonPoints: rightPoly, orientation: 'v', fixedX: ox + ow - fwInt, fixedY: 0, fw: fwInt });
    return { x: ox, y: oy, w: ow, h: oh, fw: fwInt };
  };

  const drawFrame = () => {
    const version = ++renderVersion.current;
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    const container = containerRef.current;
    const maxWidth = container ? container.clientWidth - 20 : 400;
    const maxHeight = 400;
    const layers = getAllLayers();
    const hasBaguetteOrPp =
      (orderData.frames && orderData.frames.some((f) => f.baguette_id)) ||
      (orderData.passepartouts && orderData.passepartouts.some((pp) => pp.passepartout_id)) ||
      orderData.baguette_id;
    if (!hasBaguetteOrPp) return;
    const { height, width, mats } = previewGeometry(orderData);
    const unit = 5;
    const iw = width * unit;
    const ih = height * unit;
    const widths = layers.map((layer) => baguetteWidthPixels(layer.width, unit));
    const totalInset = widths.reduce((a, b) => a + b, 0);
    const outW = Math.ceil(iw + 2 * totalInset);
    const outH = Math.ceil(ih + 2 * totalInset);
    const scale = Math.min(maxWidth / outW, maxHeight / outH, 1);
    canvas.width = outW;
    canvas.height = outH;
    canvas.style.width = outW * scale + 'px';
    canvas.style.height = outH * scale + 'px';
    const photoX = totalInset;
    const photoY = totalInset;
    const iwInt = iw;
    const ihInt = ih;
    const createPlaceholder = () => {
      const p = document.createElement('canvas');
      p.width = 64;
      p.height = DEFAULT_FRAME_WIDTH;
      p.getContext('2d').fillStyle = '#8b5cf6';
      p.getContext('2d').fillRect(0, 0, 64, DEFAULT_FRAME_WIDTH);
      return p;
    };
    const loadImage = (url) =>
      new Promise((resolve) => {
        const img = new Image();
        img.crossOrigin = 'anonymous';
        img.onload = () => resolve(img);
        img.onerror = () => resolve(createPlaceholder());
        img.src = url;
      });
    const imageUrls = [...layers.map((l) => l.image), ...mats.map((m) => m.passepartout_image)];
    const loadPainting = () =>
      paintingImage && typeof paintingImage === 'string'
        ? new Promise((resolve) => {
            const img = new Image();
            img.onload = () => resolve(img);
            img.onerror = () => resolve(null);
            img.src = paintingImage;
          })
        : Promise.resolve(null);
    Promise.all([
      ...imageUrls.map((url) => (url ? loadImage(url) : Promise.resolve(null))),
      loadPainting(),
    ]).then((results) => {
      const loadedImgs = results.slice(0, imageUrls.length);
      const photoImg = results[results.length - 1];
      if (version !== renderVersion.current) return;
      if (canvas.width !== outW || canvas.height !== outH) return;
      ctx.clearRect(0, 0, outW, outH);
      const paintingWidth = Math.min(width, ...mats.map((m) => m.windowWidth)) * unit;
      const paintingHeight = Math.min(height, ...mats.map((m) => m.windowHeight)) * unit;
      const paintingX = photoX + (iw - paintingWidth) / 2;
      const paintingY = photoY + (ih - paintingHeight) / 2;
      if (photoImg) {
        ctx.drawImage(photoImg, paintingX, paintingY, paintingWidth, paintingHeight);
      } else {
        ctx.fillStyle = '#f8f9fa';
        ctx.fillRect(photoX, photoY, iwInt, ihInt);
      }
      // Paint each sheet only outside its actual window. Both axes share one scale.
      [...mats.entries()].reverse().forEach(([index, mat]) => {
        const outerW = mat.outerWidth * unit;
        const outerH = mat.outerHeight * unit;
        const windowW = mat.windowWidth * unit;
        const windowH = mat.windowHeight * unit;
        ctx.save();
        ctx.beginPath();
        ctx.rect(photoX + (iw - outerW) / 2, photoY + (ih - outerH) / 2, outerW, outerH);
        ctx.rect(photoX + (iw - windowW) / 2, photoY + (ih - windowH) / 2, windowW, windowH);
        ctx.clip('evenodd');
        const texture = loadedImgs[layers.length + index];
        ctx.fillStyle = texture ? ctx.createPattern(texture, 'repeat') : PASSEPARTOUT_COLOR;
        ctx.fillRect(photoX, photoY, iw, ih);
        ctx.restore();
      });
      let rect = { x: photoX, y: photoY, w: iwInt, h: ihInt };
      const localCanvas = { width: outW, height: outH };
      layers.forEach((layer, index) => {
        rect = drawFrameLayer(ctx, localCanvas, {
          contentRect: rect, texImgOrCanvas: loadedImgs[index] || createPlaceholder(), fw: widths[index],
        });
      });
      if (layers.length === 0 && !mats.length && hasBaguetteOrPp) {
        ctx.strokeStyle = '#8b5cf6';
        ctx.lineWidth = DEFAULT_FRAME_WIDTH;
        ctx.strokeRect(photoX - DEFAULT_FRAME_WIDTH / 2, photoY - DEFAULT_FRAME_WIDTH / 2, iwInt + DEFAULT_FRAME_WIDTH, ihInt + DEFAULT_FRAME_WIDTH);
      }
    });
  };

  useEffect(() => {
    const hasData =
      (orderData.x1 && orderData.x2) ||
      (orderData.frames && orderData.frames.some((f) => f.baguette_id || (f.x1 && f.x2))) ||
      (orderData.passepartouts && orderData.passepartouts.some((pp) => pp.passepartout_id)) ||
      orderData.baguette_id;
    if (hasData) {
      const timeout = setTimeout(drawFrame, 100);
      return () => clearTimeout(timeout);
    }
  }, [orderData.x1, orderData.x2, orderData.frames, orderData.passepartouts, orderData.baguette_id, orderData.baguette_image, paintingImage]);

  useEffect(() => {
    const handleResize = () => {
      const hasData =
        (orderData.x1 && orderData.x2) ||
        (orderData.frames && orderData.frames.some((f) => f.baguette_id || (f.x1 && f.x2))) ||
        (orderData.passepartouts && orderData.passepartouts.some((pp) => pp.passepartout_id));
      if (hasData) setTimeout(drawFrame, 100);
    };
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, [orderData.x1, orderData.x2, orderData.frames, orderData.passepartouts, orderData.baguette_id]);

  const hasData =
    (orderData.x1 && orderData.x2) ||
    (orderData.frames && orderData.frames.some((f) => f.baguette_id || (f.x1 && f.x2))) ||
    (orderData.passepartouts && orderData.passepartouts.some((pp) => pp.passepartout_id)) ||
    orderData.baguette_id;

  return (
    <div ref={containerRef} className={showLabel ? 'shrink-0' : 'w-full'}>
      {showLabel && <p className="text-sm text-gray-500 mb-2">Предпросмотр</p>}
      <div className={`rounded-lg p-3 bg-gray-50 ${showLabel ? 'border border-gray-300' : ''}`}>
        {hasData ? (
          <div className="flex justify-center">
            <canvas ref={canvasRef} className="block rounded-lg" style={{ maxWidth: '100%', maxHeight: '400px' }} />
          </div>
        ) : (
          <div className={`flex flex-col items-center justify-center text-gray-400 text-sm ${showLabel ? 'w-40 h-32' : 'py-8'}`}>
            {!showLabel && (
              <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
            )}
            <p className={!showLabel ? 'mt-2' : ''}>Укажите размеры и выберите багет</p>
          </div>
        )}
      </div>
    </div>
  );
};
