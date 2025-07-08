import torch
import torch.nn as nn
import numpy as np
import cv2
from pathlib import Path
from torchvision.ops import nms
import torch
import torchvision

class ModelHandler:
    def __init__(self, labels, model_path="/opt/nuclio/yolo11m.pt", device=None):
        device = 'cuda' if torch.cuda.is_available() else 'cpu'
        self.device = torch.device(device)
        self.model = None
        self.labels = labels
        self.load_network(model_path)
        self.input_shape = [1, 3, 640, 640]  # Default YOLO input shape

    def load_network(self, model_path):
        try:
            # Load YOLOv11 model
            checkpoint = torch.load(model_path, map_location=self.device, weights_only=False)
            if isinstance(checkpoint, dict):
                if 'model' in checkpoint:
                    self.model = checkpoint['model']
                elif 'state_dict' in checkpoint:
                    raise NotImplementedError("Need model architecture to load state_dict")
                else:
                    self.model = checkpoint
            else:
                self.model = checkpoint
            # self.model = self.model.float()  # Ensure model is in float32
            self.model = self.model.to(self.device).eval()
            self.is_initiated = True
        except Exception as e:
            raise Exception(f"Cannot load model {model_path}: {e}")

    def letterbox(self, im, new_shape=(640, 640), color=(114, 114, 114), auto=True, scaleup=True, stride=32):
        # Resize and pad image while meeting stride-multiple constraints
        shape = im.shape[:2]  # current shape [height, width]
        if isinstance(new_shape, int):
            new_shape = (new_shape, new_shape)

        # Scale ratio (new / old)
        r = min(new_shape[0] / shape[0], new_shape[1] / shape[1])
        if not scaleup:  # only scale down, do not scale up (for better val mAP)
            r = min(r, 1.0)

        # Compute padding
        new_unpad = int(round(shape[1] * r)), int(round(shape[0] * r))
        dw, dh = new_shape[1] - new_unpad[0], new_shape[0] - new_unpad[1]  # wh padding

        if auto:  # minimum rectangle
            dw, dh = np.mod(dw, stride), np.mod(dh, stride)  # wh padding

        dw /= 2  # divide padding into 2 sides
        dh /= 2

        if shape[::-1] != new_unpad:  # resize
            im = cv2.resize(im, new_unpad, interpolation=cv2.INTER_LINEAR)
        top, bottom = int(round(dh - 0.1)), int(round(dh + 0.1))
        left, right = int(round(dw - 0.1)), int(round(dw + 0.1))
        im = cv2.copyMakeBorder(im, top, bottom, left, right, cv2.BORDER_CONSTANT, value=color)  # add border
        cv2.imwrite("padded_image.jpg", im)  # Save padded image for debugging
        return im, r, (dw, dh)

    def postprocess_results(self, results, conf_threshold=0.25, iou_threshold=0.5):
        """YOLOv11 postprocessing with NMS"""
        output = []

        results = results.permute(0, 2, 1)  # Transpose to (batch, detections, features)

        for b in range(results.shape[0]):
            boxes = []
            scores = []
            class_ids = []

            for det in results[b]:
                box = det[:4]
                class_scores = det[4:]
                class_id = torch.argmax(class_scores).item()
                conf = class_scores[class_id].item()

                if conf > conf_threshold:
                    cx, cy, w, h = box
                    x1 = cx - w / 2
                    y1 = cy - h / 2
                    x2 = cx + w / 2
                    y2 = cy + h / 2
                    boxes.append([x1, y1, x2, y2])
                    scores.append(conf)
                    class_ids.append(class_id)

            if not boxes:
                continue

            boxes_tensor = torch.tensor(boxes, dtype=torch.float32, device=self.device)
            scores_tensor = torch.tensor(scores, dtype=torch.float32, device=self.device)

            # Perform NMS per class
            final_indices = []
            for cls in np.unique(class_ids):
                cls_indices = [i for i, c in enumerate(class_ids) if c == cls]
                cls_boxes = boxes_tensor[cls_indices]
                cls_scores = scores_tensor[cls_indices]
                keep = nms(cls_boxes, cls_scores, iou_threshold)
                final_indices.extend([cls_indices[i] for i in keep])

            final_boxes = [boxes[i] for i in final_indices]
            final_scores = [scores[i] for i in final_indices]
            final_class_ids = [class_ids[i] for i in final_indices]
            output = [final_boxes, final_class_ids, final_scores]

        return output

    # def _infer(self, inputs: np.ndarray):
    #     try:
    #         img = cv2.cvtColor(inputs, cv2.COLOR_BGR2RGB)
    #         img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)  # Convert back to BGR for OpenCV
    #         # cv2.imwrite("input_image.jpg", img)  # Save input image for debugging
    #         image = img.copy()
    #         # cv2.imwrite("input_image.jpg", image)  # Save input image for debugging
    #         image, ratio, dwdh = self.letterbox(image, auto=False)
    #         image = image.transpose((2, 0, 1))
    #         image = np.expand_dims(image, 0)
    #         image = np.ascontiguousarray(image)
        
    #         im = image.astype(np.float32)
    #         im /= 255
    #         input_tensor = torch.from_numpy(im).to(self.device)
    #         print(f"Input tensor shape: {input_tensor.shape}, dtype: {input_tensor.dtype}") 
    #         # with torch.no_grad():
    #         #     detections = self.model(input_tensor)[0]

    #         detections = self.model(input_tensor)[0]  # Run inference
    #         print(f"Hello")

    #         print(f"Detections shape: {detections.shape}")

    #         processed_detections = self.postprocess_results(detections)

    #         if not processed_detections:
    #             return None

    #         boxes, labels, scores = processed_detections

    #         # Adjust boxes for padding and scaling
    #         boxes = np.array(boxes)
    #         boxes -= np.array(dwdh * 2)
    #         boxes /= ratio
    #         boxes = boxes.round().astype(np.int32)

    #         return [boxes, np.array(labels), np.array(scores)]

    #     except Exception as e:
    #         print(e)
    #         return None

    def _infer(self, inputs: np.ndarray):
        try:
            img = cv2.cvtColor(inputs, cv2.COLOR_BGR2RGB)
            # Remove the redundant second conversion - this was converting back to BGR
            # img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            
            image = img.copy()
            image, ratio, dwdh = self.letterbox(image, auto=False)
            image = image.transpose((2, 0, 1))
            image = np.expand_dims(image, 0)
            image = np.ascontiguousarray(image)
            im = image.astype(np.float32)
            im /= 255
            input_tensor = torch.from_numpy(im).to(self.device)
            
            # Convert to half precision to match model weights
            input_tensor = input_tensor.half()
            
            print(f"Input tensor shape: {input_tensor.shape}, dtype: {input_tensor.dtype}")
            
            with torch.no_grad():  # Add this back for inference
                detections = self.model(input_tensor)[0]
                
            print(f"Detections shape: {detections.shape}")
            processed_detections = self.postprocess_results(detections)
            
            if not processed_detections:
                return None
                
            boxes, labels, scores = processed_detections
            boxes = np.array(boxes)
            boxes -= np.array(dwdh * 2)
            boxes /= ratio
            boxes = boxes.round().astype(np.int32)
            return [boxes, np.array(labels), np.array(scores)]
            
        except Exception as e:
            print(f"Error in inference: {e}")
            return None

    def infer(self, image, threshold):
        print("Running inference...")
        image = np.array(image)
        image = image[:, :, ::-1].copy()
        h, w, _ = image.shape
        detections = self._infer(image)

        results = []
        if detections:
            boxes, labels, scores = detections

            for label, score, box in zip(labels, scores, boxes):
                if score >= threshold:
                    xtl = max(int(box[0]), 0)
                    ytl = max(int(box[1]), 0)
                    xbr = min(int(box[2]), w)
                    ybr = min(int(box[3]), h)

                    results.append({
                        "confidence": str(score),
                        "label": self.labels.get(label, "unknown"),
                        "points": [xtl, ytl, xbr, ybr],
                        "type": "rectangle",
                    })

        else:
            print("No valid detections to process.")
        print(f"Results: {results}")

        return results


