// All dimensions use centimetres; x1/length is height, x2/width is width.
export function previewGeometry(orderData) {
  const firstFrame = orderData.frames?.[0];
  const height = Number(firstFrame?.x1 ?? orderData.x1) || 30;
  const width = Number(firstFrame?.x2 ?? orderData.x2) || 20;
  const mats = (orderData.passepartouts || [])
    .filter((pp) => pp?.passepartout_id)
    .map((pp) => {
      const outerHeight = Math.min(height, Number(pp.passepartout_length) || height);
      const outerWidth = Math.min(width, Number(pp.passepartout_width) || width);
      return {
        ...pp,
        outerHeight, outerWidth,
        windowHeight: Math.min(outerHeight, Number(pp.window_length) || outerHeight),
        windowWidth: Math.min(outerWidth, Number(pp.window_width) || outerWidth),
      };
    })
    // Large windows are at the front, small windows are closest to the picture.
    .sort((a, b) => b.windowHeight * b.windowWidth - a.windowHeight * a.windowWidth);
  return { height, width, mats };
}
